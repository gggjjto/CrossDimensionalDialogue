import { Box, Input, Text, Image, HStack, Stack } from "@chakra-ui/react"
import { createFileRoute, useNavigate } from "@tanstack/react-router"
import { useState } from "react"
import { CiSearch } from "react-icons/ci"
import { BsChatDots, BsHeart } from "react-icons/bs"

import IndexAside from "@/components/Common/Aside"
import { InputGroup } from "@/components/ui/input-group"
import MasonryGrid from "@/components/index/MasonryGrid"
import { useEffect } from "react"
import { charactersApi } from "@/api/characters"
import type { CharacterPublic } from "@/api/characters/type"

export const Route = createFileRoute("/_layout/")({
  component: RouteComponent,
})

interface ItemCardProps {
  title: string
  author: string
  comments: number
  likes: number
  src: string
}

function ItemCard(props: ItemCardProps) {
  const [isHoverImage, setIsHoverImage] = useState(false)
  const navigate = useNavigate()

  const { title, author, comments, likes, src } = props
  return (
    <Box
      position={"relative"}
      rounded="md"
      border={"2px solid"}
      borderColor={"black"}
      overflow="hidden"
      cursor={"pointer"}
      onMouseEnter={() => setIsHoverImage(true)}
      onMouseLeave={() => setIsHoverImage(false)}
      onClick={() => navigate({ to: "/$id", params: { id: "123" } })}
    >
      {/* 背景图片 */}
      <Image
        transform={isHoverImage ? "scale(1.1)" : "scale(1)"}
        transition={"all 0.3s ease"}
        src={src}
        alt={title}
        w="full"
        h="auto"
        display="block"
      />

      {/* 渐变遮罩：覆盖整张图（上白到下透明黑），确保明显可见 */}
      <Box
        position="absolute"
        inset={0}
        pointerEvents="none"
        zIndex={1}
        backgroundImage="linear-gradient(to bottom, rgba(255,255,255,0.25) 0%, rgba(255,255,255,0.0) 40%, rgba(0,0,0,0.0) 60%, rgba(0,0,0,0.9) 100%)"
      />

      {/* 底部信息栏，覆盖在图片之上 */}
      <Box
        position="absolute"
        left={0}
        right={0}
        bottom={0}
        p={3}
        color="white"
        zIndex={2}
      >
        <Text lineClamp={2} fontWeight="medium">
          {title}
        </Text>
        <HStack gap="2" mt={2} alignItems="center">
          {/* <Avatar.Root>
            <Avatar.Fallback name={author} />
            <Avatar.Image />
          </Avatar.Root> */}
          <Stack gap="0">
            <Text fontWeight="medium">{author}</Text>
            <Box
              display={"flex"}
              gap={2}
              fontSize={"xs"}
              color={"whiteAlpha.800"}
            >
              <Text display={"flex"} alignItems={"center"} gap={1}>
                <BsChatDots />
                {comments}
              </Text>
              <Text display={"flex"} alignItems={"center"} gap={1}>
                <BsHeart />
                {likes}
              </Text>
            </Box>
          </Stack>
        </HStack>
      </Box>
    </Box>
  )
}

function RouteComponent() {
  // 角色数据与加载状态
  const [items, setItems] = useState<CharacterPublic[]>([])
  const [hasMore, setHasMore] = useState(true)
  const [skip, setSkip] = useState(0)
  const limit = 20

  const mapToCardItem = (c: CharacterPublic) => ({
    title: c.name,
    author: "",
    comments: 0,
    likes: 0,
    src: c.avatar_url || `https://picsum.photos/seed/${c.id}/400/360`,
  })

  const loadMore = async () => {
    const res = await charactersApi.getPublicCharacters({ skip, limit })
    const list = res.characters
    const next = [...items, ...list]
    setItems(next)
    setSkip(skip + list.length)
    if (next.length >= res.total || list.length < limit) setHasMore(false)
  }

  useEffect(() => {
    // 首次加载
    loadMore()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  return (
    <Box w={"full"} h={"full"} display={"flex"}>
      <IndexAside />

      <Box
        flex={"1"}
        overflow={"auto"}
        display={"flex"}
        flexDirection={"column"}
        alignItems={"center"}
        px={35}
        id="scrollable-content"
      >
        <Box
          display={"flex"}
          justifyContent={"center"}
          position={"sticky"}
          top={0}
          zIndex={10}
          w={"full"}
          p={4}
          bg={"bg.default"}
        >
          <InputGroup w={"50%"} startElement={<CiSearch />}>
            <Input placeholder="搜索AI角色..." variant="subtle" />
          </InputGroup>
        </Box>

        <Box w={"100%"} h={"100%"} py={4}>
          <Box w={"100%"} lineHeight={"1.5"}>
            <Text fontWeight={"bold"} fontSize={"xl"}>
              发现AI角色
            </Text>
            <Text className="text-muted">与各种AI角色开始对话</Text>
          </Box>
        </Box>

        <Box w={"100%"} h={"100%"} pb={10}>
          <MasonryGrid
            items={items}
            getKey={(_, i) => i}
            gutter="2px"
            hasMore={hasMore}
            onLoadMore={loadMore}
            loader={
              <Text textAlign="center" py={4}>
                加载中...
              </Text>
            }
            endMessage={
              <Text textAlign="center" py={4}>
                没有更多了
              </Text>
            }
            scrollableTarget="scrollable-content"
            render={(item) => {
              const card = mapToCardItem(item as unknown as CharacterPublic)
              return (
                <ItemCard
                  title={card.title}
                  author={card.author}
                  comments={card.comments}
                  likes={card.likes}
                  src={card.src}
                />
              )
            }}
          />
        </Box>
      </Box>
    </Box>
  )
}

// 已改为从后端加载公开角色列表
