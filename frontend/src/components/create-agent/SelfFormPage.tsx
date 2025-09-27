import { Container, Flex, HStack, Text, Textarea, Box, Image } from "@chakra-ui/react"
import { Controller, useForm } from "react-hook-form"
import { useEffect } from "react"

import Divide from "@/components/ui/divide"
import { Field } from "@/components/ui/field"
import { Button } from "@/components/ui/button"
import { Radio, RadioGroup } from "@/components/ui/radio"
import { styleRules } from "@/utils/rules"
import { useSelfAgent } from "@/contexts/SelfAgentContext"
import { imageApi } from "@/api/image"
import { charactersApi } from "@/api/characters"

export interface SelfForm {
  style: "" | "real" | "anime"
  description: string
}

export default function SelfFormPage() {
  const { state, dispatch } = useSelfAgent()

  // 表单：风格与人物形象描述
  const {
    register,
    handleSubmit,
    control,
    watch,
    formState: { errors, isSubmitting },
  } = useForm<SelfForm>({
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues: state.selfFormData,
  })

  const current = watch()
  const canGenerate =
    current.style !== "" && current.description.trim().length > 0

  // 同步表单到上下文，避免跨页丢失
  useEffect(() => {
    const subscription = watch((v) => {
      const values = v as unknown as SelfForm
      dispatch({ type: "SET_SELF_FORM", payload: values })
    })
    return () => subscription.unsubscribe()
  }, [watch, dispatch])

  // 生成图片业务逻辑
  const onGenerate = async (data: SelfForm) => {
    dispatch({ type: "SET_SELF_FORM", payload: data })
    dispatch({ type: "SET_GENERATING", payload: true })
    try {
      // 使用描述作为 prompt 生成图片（真实接口）
      const style = data.style === "anime" ? "anime" : "realistic"
      const res1 = await imageApi.generate({ prompt: data.description, style })
      const res2 = await imageApi.generate({ prompt: data.description, style })
      const images = [res1.url, res2.url].filter(Boolean)
      if (images.length > 0) {
        dispatch({ type: "SET_GENERATED_IMAGES", payload: images as string[] })
      }
    } finally {
      dispatch({ type: "SET_GENERATING", payload: false })
    }
  }

  // 重新生成图片业务逻辑
  const onRegenerate = async () => {
    dispatch({ type: "SET_GENERATING", payload: true })
    try {
      const style = (state.selfFormData.style || "real") === "anime" ? "anime" : "realistic"
      const res1 = await imageApi.generate({ prompt: state.selfFormData.description, style })
      const res2 = await imageApi.generate({ prompt: state.selfFormData.description, style })
      const images = [res1.url, res2.url].filter(Boolean)
      if (images.length > 0) {
        dispatch({ type: "SET_GENERATED_IMAGES", payload: images as string[] })
      }
    } finally {
      dispatch({ type: "SET_GENERATING", payload: false })
    }
  }

  return (
    <Flex
      h={"full"}
      w={"full"}
      justify={"space-between"}
      align={"center"}
      gap={4}
    >
      {/* 左侧：表单区 */}
      <Flex
        direction={"column"}
        justify={"center"}
        h={"full"}
        w={"40%"}
        gap={4}
      >
        <Container
          as="form"
          onSubmit={(e) => e.preventDefault()}
          maxW="600px"
          w={"full"}
          spaceY={6}
          bg={"bg.default"}
          borderRadius={"md"}
          padding={4}
          boxShadow="sm"
        >
          <Field
            label="绘图风格选择"
            required
            invalid={!!errors.style}
            errorText={errors.style?.message}
          >
            <Controller
              name="style"
              control={control}
              rules={styleRules()}
              render={({ field }) => (
                <RadioGroup
                  value={field.value}
                  onValueChange={(details) => field.onChange(details.value)}
                  onBlur={field.onBlur}
                  orientation="horizontal"
                >
                  <HStack gap="6">
                    <Radio value="real">真人</Radio>
                    <Radio value="anime">动漫</Radio>
                  </HStack>
                </RadioGroup>
              )}
            />
          </Field>

          <Field
            label="人物形象描述"
            required
            invalid={!!errors.description}
            errorText={errors.description?.message}
          >
            <Textarea
              {...register("description", {
                required: "请描述人物形象",
                minLength: { value: 2, message: "描述至少2个字符" },
              })}
              placeholder={
                "描述性别、发型、面部表情、肤色、服饰等形象特征或绘图风格特征，如：金发女生，嘴角带笑，穿着穿着军训服，秋日晴朗，树上落下枫叶，需要水彩画风格图像"
              }
              bg={"bg.muted"}
              minH={490}
              aria-invalid={!!errors.description}
            />
          </Field>

          <Flex justify={"center"}>
            <Button
              rounded={"full"}
              px={20}
              disabled={!canGenerate}
              loading={isSubmitting || state.isGenerating}
              variant={"outline"}
              bg={"bg.default"}
              _hover={{ bg: "bg.muted" }}
              onClick={() => {
                if (state.generatedImages.length > 0) {
                  onRegenerate()
                } else {
                  handleSubmit(onGenerate)()
                }
              }}
            >
              {state.generatedImages.length > 0 ? "重新生成图片" : "生成图片"}
            </Button>
          </Flex>
        </Container>
      </Flex>

      <Divide h={"full"} w={"1px"} bg={"accent.quaternary"}></Divide>

      {/* 右侧：预览区 */}
      <Flex direction={"column"} justify={"center"} h={"full"} w={"60%"}>
        {state.generatedImages.length > 0 ? (
          <Flex
            gap={4}
            justify={"center"}
            align={"center"}
            direction={"column"}
          >
            <Text fontSize={"2xl"} fontWeight={600} textAlign={"center"}>
              生成的角色形象
            </Text>
            <Flex gap={4} justify={"center"} align={"center"}>
              {state.generatedImages.map((src, index) => {
                const isSelected = state.selectedImage === src
                return (
                  <Box
                    key={index}
                    position={"relative"}
                    borderRadius={"md"}
                    overflow={"hidden"}
                    boxShadow={isSelected ? "xl" : "lg"}
                    border={"3px solid"}
                    borderColor={isSelected ? "blue.400" : "gray.200"}
                    cursor={"pointer"}
                    onClick={() => dispatch({ type: "SET_SELECTED_IMAGE", payload: src })}
                  >
                    <Image
                      src={src}
                      alt={`生成的角色形象 ${index + 1}`}
                      w={"300px"}
                      h={"400px"}
                      objectFit={"cover"}
                    />
                  </Box>
                )
              })}
            </Flex>
            <Text color={"fg.muted"} fontSize={"sm"} textAlign={"center"}>
              滑动到下一页完善角色信息
            </Text>
          </Flex>
        ) : (
          <Flex
            align={"center"}
            justify={"center"}
            direction={"column"}
            lineHeight={"1.5"}
            bg={"bg.default"}
            borderRadius={"md"}
            padding={4}
            h={"85%"}
          >
            <Text fontSize={"2xl"} fontWeight={550}>
              角色形象会在这里展示哟~
            </Text>
            <Text color={"fg.muted"}>赶快去描述你想创建的角色吧~</Text>
          </Flex>
        )}
      </Flex>
    </Flex>
  )
}
