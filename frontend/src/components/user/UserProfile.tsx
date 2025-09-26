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
import { useState } from "react"
import { FiEdit, FiUpload } from "react-icons/fi"

import UserStats from "@/components/user/UserStats"

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
    username: "张小明",
    gender: "male",
    uid: "1111111",
    email: "zhang@example.com",
    bio: "热爱AI技术的产品经理,喜欢尝试各种有趣的AI工具。",
  })

  const handleEdit = () => {
    setIsEditing(!isEditing)
  }

  const handleSave = () => {
    // TODO: 保存用户信息到后端
    setIsEditing(false)
  }

  const handleCancel = () => {
    setIsEditing(false)
  }

  return (
    <Stack gap={8} w="100%" maxW="525px">
      {/* 用户头像 */}
      <Box position="relative" alignSelf="center">
        <Avatar.Root size="full">
          <Avatar.Image src="https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=150&h=150&fit=crop&crop=face" />
          <Avatar.Fallback name={userInfo.username} />
        </Avatar.Root>
        <Button
          position="absolute"
          bottom={0}
          right={0}
          size="md"
          borderRadius="full"
          bg="accent.default"
          color="accent.foreground"
          _hover={{ bg: "accent.emphasis" }}
          p={2}
          minW="auto"
          h="auto"
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


      {/* 使用统计卡片 */}
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
