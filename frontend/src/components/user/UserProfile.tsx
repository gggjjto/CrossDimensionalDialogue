import {
  Avatar,
  Box,
  Button,
  Field,
  Flex,
  Input,
  Portal,
  Select,
  Stack,
  Text,
  Textarea,
  createListCollection,
} from "@chakra-ui/react"
import { useEffect, useRef, useState } from "react"
import { FiEdit, FiUpload } from "react-icons/fi"

import UserStats from "@/components/user/UserStats"
import { imageApi } from "@/api/image"
import { toaster } from "@/components/ui/toaster"
import { userApi } from "@/api/user"

// 性别选项集合
const genderOptions = createListCollection({
  items: [
    { label: "男", value: "male" },
    { label: "女", value: "female" },
    { label: "其他", value: "other" },
  ],
})

export default function UserProfile() {
  const [isEditing, setIsEditing] = useState(false)
  const [userInfo, setUserInfo] = useState({
    username: "",
    gender: "male",
    uid: "",
    email: "",
    bio: "",
    avatar_url: "",
    created_at: "",
    character_count: 0,
    conversation_count: 0,
  })

  useEffect(() => {
    ;(async () => {
      try {
        const me = await userApi.me()
        setUserInfo({
          username: me.full_name || me.email?.split('@')[0] || "",
          gender: me.gender || "male",
          uid: me.id,
          email: me.email || "",
          bio: me.bio || "",
          avatar_url: me.avatar_url || "",
          created_at: me.created_at,
          character_count: me.character_count ?? 0,
          conversation_count: me.conversation_count ?? 0,
        })
      } catch {
        // 忽略加载失败
      }
    })()
  }, [])

  const handleEdit = () => {
    setIsEditing(!isEditing)
  }

  const handleSave = async () => {
    try {
      await userApi.updateMe({
        full_name: userInfo.username,
        avatar_url: userInfo.avatar_url,
        bio: userInfo.bio,
        gender: userInfo.gender as any,
      })
      setIsEditing(false)
    } catch {
      // 简单失败回退
    }
  }

  const handleCancel = () => {
    setIsEditing(false)
  }

  // 头像上传（隐藏 input ref）
  const fileInputRef = useRef<HTMLInputElement | null>(null)

  const onFileChange: React.ChangeEventHandler<HTMLInputElement> = async (e) => {
    const file = e.target.files?.[0]
    if (!file) return
    if (file.size > 2 * 1024 * 1024) {
      toaster.error({ title: "图片过大", description: "请上传不超过 2MB 的图片" })
      e.target.value = ""
      return
    }
    const previous = userInfo.avatar_url
    const tempUrl = URL.createObjectURL(file)
    setUserInfo((u) => ({ ...u, avatar_url: tempUrl }))
    try {
      const res = await imageApi.upload(file)
      await userApi.updateMe({ avatar_url: res.url })
      setUserInfo((u) => ({ ...u, avatar_url: res.url }))
      toaster.success({ title: "头像已更新" })
    } catch (e: any) {
      setUserInfo((u) => ({ ...u, avatar_url: previous }))
      toaster.error({ title: "上传失败", description: e?.message || "请稍后重试" })
    } finally {
      try { URL.revokeObjectURL(tempUrl) } catch {}
      e.target.value = ""
    }
  }

  return (
    
    <Stack gap={8} w="100%" maxW="525px">
      {/* 用户头像 */}
      <Box position="relative" alignSelf="center">
        <Avatar.Root w="120px" h="120px" borderRadius="full">
          <Avatar.Image src={userInfo.avatar_url || "https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=150&h=150&fit=crop&crop=face"} />
          <Avatar.Fallback name={userInfo.username || "用户"} />
        </Avatar.Root>
        <input
          ref={fileInputRef}
          id="avatar-file-input"
          type="file"
          accept="image/*"
          style={{ display: "none" }}
          onChange={onFileChange}
        />
        <Button
          position="absolute"
          bottom={0}
          right={0}
          size="sm"
          borderRadius="full"
          bg="accent.default"
          color="accent.foreground"
          _hover={{ bg: "accent.emphasis" }}
          p={2}
          minW="auto"
          h="auto"
          onClick={() => fileInputRef.current?.click()}
        >
          <FiUpload size={16} />
        </Button>
      </Box>

      {/* 个人信息卡片 */}
      <Box
        bg="surface.default"
        borderRadius="md"
        p={6}
        borderWidth="1px"
        borderColor="border.default"
        shadow="sm"
      >
        <Flex justify="space-between" align="center" mb={4}>
          <Text fontSize="lg" fontWeight="bold">
            个人信息
          </Text>
          {!isEditing ? (
            <Button
              bg="accent.default"
              color="accent.foreground"
              size="sm"
              onClick={handleEdit}
              _hover={{ bg: "accent.emphasis" }}
            >
              <FiEdit style={{ marginRight: '8px' }} />
              编辑
            </Button>
          ) : (
            <Flex gap={2}>
              <Button size="sm" onClick={handleSave}>
                保存
              </Button>
              <Button variant="outline" size="sm" onClick={handleCancel}>
                取消
              </Button>
            </Flex>
          )}
        </Flex>

        <Stack gap={5}>
          {/* 用户名和性别在同一行 */}
          <Flex gap={4}>
            <Field.Root flex="1">
              <Field.Label fontSize="sm" color="fg.default" mb={2}>用户名</Field.Label>
              <Input
                value={userInfo.username}
                onChange={(e) =>
                  setUserInfo({ ...userInfo, username: e.target.value })
                }
                disabled={!isEditing}
                bg="surface.default"
                border="1px solid"
                borderColor="border.default"
                borderRadius="md"
                color="fg.default"
                _disabled={{ bg: "bg.muted", color: "fg.default", opacity: 1 }}
                _focus={{ borderColor: "accent.default" }}
              />
            </Field.Root>
            <Field.Root flex="1">
              <Field.Label fontSize="sm" color="fg.default" mb={2}>性别</Field.Label>
              <Select.Root 
                variant="outline"
                collection={genderOptions}
                value={[userInfo.gender]}
                onValueChange={(e) => setUserInfo({ ...userInfo, gender: e.value[0] || "" })}
                disabled={!isEditing}
              >
                <Select.HiddenSelect />
                <Select.Control>
                  <Select.Trigger
                    bg={isEditing ? "surface.default" : "bg.muted"}
                    border="1px solid"
                    borderColor="border.default"
                    borderRadius="md"
                    color="fg.default"
                    _disabled={{ bg: "bg.muted", color: "fg.default", opacity: 1 }}
                    _focus={{ borderColor: "accent.default" }}
                  >
                    <Select.ValueText placeholder="请选择性别" />
                  </Select.Trigger>
                  <Select.IndicatorGroup>
                    <Select.Indicator />
                  </Select.IndicatorGroup>
                </Select.Control>
                <Portal>
                  <Select.Positioner>
                    <Select.Content>
                      {genderOptions.items.map((option) => (
                        <Select.Item item={option} key={option.value}>
                          {option.label}
                          <Select.ItemIndicator />
                        </Select.Item>
                      ))}
                    </Select.Content>
                  </Select.Positioner>
                </Portal>
              </Select.Root>
            </Field.Root>
          </Flex>

          {/* UID和邮箱在同一行 */}
          <Flex gap={4}>
            <Field.Root flex="1">
              <Field.Label fontSize="sm" color="fg.default" mb={2}>UID</Field.Label>
              <Input 
                value={userInfo.uid} 
                disabled 
                bg="bg.muted"
                border="1px solid"
                borderColor="border.default"
                borderRadius="md"
                color="fg.default"
                _disabled={{ bg: "bg.muted", color: "fg.default", opacity: 1 }}
              />
            </Field.Root>
            <Field.Root flex="1">
              <Field.Label fontSize="sm" color="fg.default" mb={2}>邮箱</Field.Label>
              <Input
                value={userInfo.email}
                onChange={(e) =>
                  setUserInfo({ ...userInfo, email: e.target.value })
                }
                disabled={!isEditing}
                bg="surface.default"
                border="1px solid"
                borderColor="border.default"
                borderRadius="md"
                color="fg.default"
                _disabled={{ bg: "bg.muted", color: "fg.default", opacity: 1 }}
                _focus={{ borderColor: "accent.default" }}
              />
            </Field.Root>
          </Flex>

          {/* 个人简介 */}
          <Field.Root>
            <Field.Label fontSize="sm" color="fg.default" mb={2}>个人简介</Field.Label>
            <Textarea
              value={userInfo.bio}
              onChange={(e) => setUserInfo({ ...userInfo, bio: e.target.value })}
              disabled={!isEditing}
              rows={4}
              resize="none"
              bg="surface.default"
              border="1px solid"
              borderColor="border.default"
              borderRadius="md"
              color="fg.default"
              _disabled={{ bg: "bg.muted", color: "fg.default", opacity: 1 }}
              _focus={{ borderColor: "accent.default" }}
            />
          </Field.Root>
        </Stack>
      </Box>


      {/* 使用统计卡片（恢复为之前的UI） */}
      <Box
        bg="surface.default"
        borderRadius="md"
        p={6}
        borderWidth="1px"
        borderColor="border.default"
        shadow="sm"
      >
        <UserStats />
      </Box>
    </Stack>
  )
}
