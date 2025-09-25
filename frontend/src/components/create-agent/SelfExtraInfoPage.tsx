import { Container, Flex, Text } from "@chakra-ui/react"

import { Button } from "@/components/ui/button"
import ExtraInfoForm from "./ExtraInfoForm"
import { useSelfAgent } from "@/contexts/SelfAgentContext"

export default function SelfExtraInfoPage() {
  const { state, dispatch } = useSelfAgent()

  // 创建智能体业务逻辑
  const createAgent = async () => {
    if (!state.isExtraFormValid) return

    dispatch({ type: "SET_CREATING", payload: true })
    try {
      // eslint-disable-next-line no-console
      console.log("创建智能体", {
        ...state.selfFormData,
        ...state.extraData,
        generatedImages: state.generatedImages,
      })

      // 模拟 API 调用
      await new Promise((resolve) => setTimeout(resolve, 1000))

      // 这里可以调用创建智能体的 API
      // 成功后可以跳转或显示成功消息
    } finally {
      dispatch({ type: "SET_CREATING", payload: false })
    }
  }

  return (
    <Flex
      h={"full"}
      w={"full"}
      justify={"center"}
      align={"flex-start"}
      pt={8}
      overflowY={"auto"}
    >
      <Container
        maxW="800px"
        w={"full"}
        bg={"bg.default"}
        borderRadius={"md"}
        padding={6}
        boxShadow="sm"
        mb={8}
      >
        <Text fontSize={"2xl"} fontWeight={600} mb={6} textAlign={"center"}>
          完善角色信息
        </Text>

        <ExtraInfoForm mode="self" />

        <Flex justify={"center"} mt={8}>
          <Button
            rounded={"full"}
            px={12}
            disabled={!state.isExtraFormValid}
            loading={state.isCreating}
            variant={"outline"}
            onClick={createAgent}
          >
            创建智能体
          </Button>
        </Flex>
      </Container>
    </Flex>
  )
}
