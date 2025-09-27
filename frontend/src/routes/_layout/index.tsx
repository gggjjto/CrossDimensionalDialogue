import {
  Box,
  Input,
  Text,
  Image,
  HStack,
  Stack,
  Spinner,
} from "@chakra-ui/react"
import { createFileRoute, useNavigate } from "@tanstack/react-router"
import { useState } from "react"
import { CiSearch } from "react-icons/ci"
import { BsChatDots, BsHeart } from "react-icons/bs"
import { useDebounce } from "ahooks"

import IndexAside from "@/components/Common/Aside"
import { InputGroup } from "@/components/ui/input-group"
import MasonryGrid from "@/components/index/MasonryGrid"
import { useAgentList } from "@/hooks/useAgentList"
import type { CharacterPublic } from "@/api/characters/type"
import EmptyState from "@/components/user/EmptyState"

export const Route = createFileRoute("/_layout/")({
  component: RouteComponent,
})

function ItemCard(props: CharacterPublic) {
  const [isHoverImage, setIsHoverImage] = useState(false)
  const navigate = useNavigate()

  const { name, short_bio, avatar_url } = props
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
        src={avatar_url}
        alt={name}
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
          {name}
        </Text>
        <HStack gap="2" mt={2} alignItems="center">
          {/* <Avatar.Root>
            <Avatar.Fallback name={author} />
            <Avatar.Image />
          </Avatar.Root> */}
          <Stack gap="0">
            <Text fontWeight="medium">{short_bio}</Text>
            <Box
              display={"flex"}
              gap={2}
              fontSize={"xs"}
              color={"whiteAlpha.800"}
            >
              <Text display={"flex"} alignItems={"center"} gap={1}>
                <BsChatDots />
                {0}
              </Text>
              <Text display={"flex"} alignItems={"center"} gap={1}>
                <BsHeart />
                {0}
              </Text>
            </Box>
          </Stack>
        </HStack>
      </Box>
    </Box>
  )
}

function RouteComponent() {
  const [searchInput, setSearchInput] = useState("")

  const debouncedSearchInput = useDebounce(searchInput, { wait: 500 })

  // 使用自定义钩子管理角色列表数据
  const {
    characters,
    isLoading: isLoadingList,
    hasMore,
    isFetchingNextPage,
    loadMore,
  } = useAgentList(debouncedSearchInput)

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
          <InputGroup
            w={"50%"}
            startElement={
              <CiSearch
                onClick={() => setSearchInput(searchInput.trim())}
                style={{ cursor: "pointer" }}
              />
            }
          >
            <Input
              placeholder="搜索AI角色..."
              variant="subtle"
              value={searchInput}
              onChange={(e) => setSearchInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") {
                  setSearchInput(searchInput.trim())
                }
              }}
            />
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
          {isLoadingList ? (
            <Box
              w={"100%"}
              display={"flex"}
              alignItems={"center"}
              justifyContent={"center"}
            >
              <Spinner />
            </Box>
          ) : characters && characters.length > 0 ? (
            <MasonryGrid
              items={characters ?? []}
              getKey={(_, i) => i}
              gutter="2px"
              hasMore={hasMore}
              onLoadMore={loadMore}
              loader={
                <Text textAlign="center" py={4}>
                  {isFetchingNextPage ? "加载中..." : "加载更多..."}
                </Text>
              }
              endMessage={
                <Text textAlign="center" py={4}>
                  没有更多了
                </Text>
              }
              scrollableTarget="scrollable-content"
              render={(item) => {
                return <ItemCard {...item} />
              }}
            />
          ) : (
            <EmptyState
              title="这里什么也没有~"
              subtitle="赶快去选择你想创建的角色吧~"
              actionText="点击去创建→"
              actionLink="/create-agent"
              minH={0}
            />
          )}
        </Box>
      </Box>
    </Box>
  )
}
