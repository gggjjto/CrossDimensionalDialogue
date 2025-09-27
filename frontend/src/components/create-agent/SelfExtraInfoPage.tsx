import { Container, Flex, Text } from "@chakra-ui/react"

import { Button } from "@/components/ui/button"
import ExtraInfoForm from "./ExtraInfoForm"
import { useSelfAgent } from "@/contexts/SelfAgentContext"
import { charactersApi } from "@/api/characters"
import { conversationsApi } from "@/api/conversations"
import { useNavigate } from "@tanstack/react-router"

export default function SelfExtraInfoPage() {
  const { state, dispatch } = useSelfAgent()
  const navigate = useNavigate()

  // 创建智能体业务逻辑
  const createAgent = async () => {
    if (!state.isExtraFormValid) return

    dispatch({ type: "SET_CREATING", payload: true })
    try {
      const name = state.extraData.nickname?.trim() || "自定义角色"
      const short_bio = state.extraData.biography?.trim() || state.extraData.publicInfo || ""
      const persona_text = state.extraData.setting?.trim() || ""
      const avatar_url = state.selectedImage || state.generatedImages[0]

      const created = await charactersApi.createCharacter({
        name,
        short_bio,
        persona_text,
        example_lines: state.extraData.openingLine ? [state.extraData.openingLine] : [],
        source: "user-self",
        is_active: true,
        is_public: true,
        ...(avatar_url ? { avatar_url } : {}),
      })

      // 若已生成图片，调用角色图片生成接口或直接更新（此处简化：后端支持在创建时自动生成/或稍后生成）
      // 后端若未自动生成头像，则在后续页面引导补充头像。这里保留所选URL在上下文中以便后续使用。

      dispatch({ type: "SET_CREATED_CHARACTER_ID", payload: String(created.id) })

      // 创建会话并写入开场白
      const conv = await conversationsApi.createConversation({
        title: `${name} 的对话`,
        character_id: String(created.id),
        description: state.extraData.publicInfo || undefined,
        settings: {
          enable_tts: false,
          language: "zh-CN",
        },
      })
      if (state.extraData.openingLine) {
        await conversationsApi.createMessage(String(conv.id), {
          sender_type: "character",
          content: state.extraData.openingLine,
        })
      }
      navigate({ to: "/$id", params: { id: String(conv.id) } })
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
