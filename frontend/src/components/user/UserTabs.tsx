import { Box, Flex, Text } from "@chakra-ui/react"
import { useState } from "react"

import AgentList from "@/components/user/AgentList"
import EmptyState from "@/components/user/EmptyState"

export default function UserTabs() {
  const [activeTab, setActiveTab] = useState<"created" | "chatted">("created")

  const innerTabs = [
    {
      id: "created" as const,
      label: "创建的智能体",
    },
    {
      id: "chatted" as const,
      label: "聊过的智能体",
    },
  ]

  // 模拟数据
  const createdAgents = [
    {
      id: "1",
      title: "小熙",
      slogan: "我是小熙，有什么我可以帮助你的吗？",
      imageSrc: "/assets/images/agent.png"      
    },
    {
      id: "2", 
      title: "小美",
      slogan: "我是小美，有什么我可以帮助你的吗？",
      imageSrc: "/assets/images/agent1.png"
    },
    {
      id: "3",
      title: "标题", 
      slogan: "宣传语",
      imageSrc: "/assets/images/agent.png"
    }
  ]

  const chattedAgents = [
    {
      id: "4",
      title: "小美",
      slogan: "我是小美，有什么我可以帮助你的吗？",
      imageSrc: "/assets/images/agent.png"
    }
  ]

  return (
    <Box bg="bg.muted" h="100vh" position="relative" display="flex" flexDirection="column">
      {/* 左侧分隔线 */}
      <Box
        position="absolute"
        left={0}
        top="10%"
        bottom="10%"
        w="1px"
        bg="border.default"
      />
      
      {/* 外层标签容器 - 居中 */}
      <Flex justify="center" mb={8} pt={100}>
        <Box
          bg="bg.muted"
          borderRadius="lg"
          border="1px solid"
          borderColor="border.default"
          shadow="sm"
          p={1}
          display="flex"
          position="relative"
          h="65px" // 与头像相同的高度
          alignItems="center"
        >
          {/* 背景滑动条 */}
          <Box
            position="absolute"
            top={0}
            bottom={0}
            left={activeTab === "created" ? "0" : "50%"}
            right={activeTab === "created" ? "50%" : "0"}
            bg="surface.default"
            borderRadius="md"
            transition="all 0.3s ease"
            zIndex={1}
          />
          
          {/* 内层标签 */}
          {innerTabs.map((tab) => (
            <Box
              key={tab.id}
              flex="1"
              px={6}
              py={3}
              borderRadius="md"
              cursor="pointer"
              color={activeTab === tab.id ? "fg.default" : "fg.muted"}
              onClick={() => setActiveTab(tab.id)}
              transition="color 0.3s ease"
              fontWeight="medium"
              position="relative"
              zIndex={2}
              display="flex"
              alignItems="center"
              justifyContent="center"
              minW="600px"
            >
              <Text>{tab.label}</Text>
            </Box>
          ))}
        </Box>
      </Flex>

      {/* 标签页内容 */}
      <Box flex="1" px={6} py={4} overflowY="auto">
        {activeTab === "created" && (
          createdAgents.length > 0 ? (
            <AgentList agents={createdAgents} showCreateLink={true} />
          ) : (
            <EmptyState
              title="这里什么也没有~"
              subtitle="赶快去选择你想创建的角色吧~"
              actionText="点击去创建→"
              actionLink="/create-agent"
            />
          )
        )}
        {activeTab === "chatted" && (
          chattedAgents.length > 0 ? (
            <AgentList agents={chattedAgents} showCreateLink={false} />
          ) : (
            <EmptyState
              title="这里什么也没有~"
              subtitle="赶快去和喜欢的角色聊天吧~"
              actionText="点击去创建→"
              actionLink="/create-agent"
            />
          )
        )}
      </Box>
    </Box>
  )
}
