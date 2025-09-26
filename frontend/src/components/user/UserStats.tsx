import { Box, Flex, Stack, Text } from "@chakra-ui/react"

export default function UserStats() {
  const stats = [
    {
      label: "创建的智能体",
      value: "3",
    },
    {
      label: "对话次数",
      value: "127",
    },
    {
      label: "注册时间",
      value: "2024-01-15",
    },
  ]

  return (
    <Box>
      <Text fontSize="lg" fontWeight="bold" mb={4}>
        使用统计
      </Text>
      <Stack gap={3}>
        {stats.map((stat, index) => (
          <Flex key={index} justify="space-between" align="center">
            <Text color="fg.muted">{stat.label}</Text>
            <Text fontWeight="medium">{stat.value}</Text>
          </Flex>
        ))}
      </Stack>
    </Box>
  )
}
