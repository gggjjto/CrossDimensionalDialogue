import {
  Center,
  Container,
  Flex,
  HStack,
  Text,
  Textarea,
} from "@chakra-ui/react"
import { createFileRoute } from "@tanstack/react-router"
import { Controller, useForm } from "react-hook-form"
import { useEffect, useState } from "react"

import Divide from "@/components/ui/divide"
import { Field } from "@/components/ui/field"
import { Button } from "@/components/ui/button"
import { Radio, RadioGroup } from "@/components/ui/radio"
import { ipSourceRules, roleNameRules, styleRules } from "@/utils/rules"
import ExtraInfoForm from "../../../components/create-agent/ExtraInfoForm"
import { useSelfAgent } from "@/contexts/SelfAgentContext"

export const Route = createFileRoute("/create-agent/_layout/ip")({
  component: RouteComponent,
})

export interface CreateAgentForm {
  ipSource: string
  roleName: string
  style: "" | "real" | "anime"
}

function RouteComponent() {
  const { state, dispatch } = useSelfAgent()

  // 设置模式为 ip
  useEffect(() => {
    dispatch({ type: "SET_MODE", payload: "ip" })
  }, [dispatch])
  // 父表单最近一次成功提交的快照（角色生成）
  const [lastParentSubmitted, setLastParentSubmitted] =
    useState<CreateAgentForm | null>(null)
  // 父+子最近一次成功提交的快照（创建智能体）
  const [lastAllSubmitted, setLastAllSubmitted] = useState<
    (CreateAgentForm & typeof state.extraData) | null
  >(null)

  const {
    register,
    handleSubmit,
    control,
    watch,
    formState: { errors, isSubmitting },
  } = useForm<CreateAgentForm>({
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues: state.ipFormData,
  })

  // 当前父表单值
  const current = watch()

  // 同步父表单到上下文
  useEffect(() => {
    const subscription = watch((v) => {
      const values = v as unknown as CreateAgentForm
      dispatch({ type: "SET_IP_FORM", payload: values })
    })
    return () => subscription.unsubscribe()
  }, [watch, dispatch])
  const filled =
    current.ipSource.trim().length > 0 &&
    current.roleName.trim().length > 0 &&
    current.style !== ""

  // 提交后必须修改才能再次提交
  const changedParentSinceSubmit = lastParentSubmitted
    ? JSON.stringify(current) !== JSON.stringify(lastParentSubmitted)
    : true
  const mergedCurrent = { ...current, ...state.extraData }
  const changedAllSinceSubmit = lastAllSubmitted
    ? JSON.stringify(mergedCurrent) !== JSON.stringify(lastAllSubmitted)
    : true

  const canSubmitGenerate = Boolean(filled && changedParentSinceSubmit)
  const canSubmitCreate = Boolean(
    filled && changedAllSinceSubmit && state.isExtraFormValid
  )

  // 提交处理（此处为占位，后续可接入后端/下一步）
  // 角色生成：仅父表单数据
  const onGenerate = (data: CreateAgentForm) => {
    if (!canSubmitGenerate) return
    // eslint-disable-next-line no-console
    console.log({ ...data })
    dispatch({ type: "SET_IP_FORM", payload: data })
    setLastParentSubmitted({ ...data })
  }

  // 创建智能体：父+子数据
  const onCreateAgent = (data: CreateAgentForm) => {
    if (!canSubmitCreate) return
    const payload = { ...data, ...state.extraData }
    // eslint-disable-next-line no-console
    console.log(payload)
    setLastAllSubmitted(payload)
  }

  return (
    <Flex
      h={"90%"}
      w={"full"}
      justify={"space-between"}
      align={"center"}
      gap={4}
    >
      <Flex direction={"column"} justify={"center"} h={"full"} w={"1/4"}>
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
          <Text color={"fg.muted"}>赶快去选择你想创建的角色吧~</Text>
        </Flex>

        <Button
          marginTop={5}
          variant="outline"
          rounded={"full"}
          bg={"bg.default"}
          _hover={{ bg: "bg.muted" }}
          onClick={() => {}}
        >
          重新生成图片
        </Button>
        <Text
          marginTop={2}
          textAlign={"center"}
          color={"fg.muted"}
          fontSize={"xs"}
        >
          可以在右上角"绘图风格选择"处选择绘图风格
        </Text>
      </Flex>

      <Divide h={"full"} w={"1px"} bg={"accent.quaternary"}></Divide>

      <Flex
        h={"full"}
        overflowY={"auto"}
        w={"3/4"}
        direction={"column"}
        align={"center"}
        gap={4}
      >
        <Container
          as="form"
          onSubmit={(e) => e.preventDefault()}
          maxW="800px"
          w={"full"}
          spaceY={6}
          bg={"bg.default"}
          borderRadius={"md"}
          padding={4}
          boxShadow="sm"
        >
          {/* IP来源 */}
          <Field
            label="IP来源"
            required
            invalid={!!errors.ipSource}
            errorText={errors.ipSource?.message}
          >
            <Textarea
              {...register("ipSource", ipSourceRules())}
              placeholder={
                "请描述IP的来源，如：需要创建一个角色叫哈利波特，可以在此处填写“哈利波特与魔法石的小说”或者“哈利波特与死亡圣器电影”"
              }
              bg={"bg.muted"}
              aria-invalid={!!errors.ipSource}
            />
          </Field>

          <Field
            label="角色名称"
            required
            invalid={!!errors.roleName}
            errorText={errors.roleName?.message}
          >
            <Textarea
              placeholder={`请填写你要创建的IP名称，如：哈利波特 \n限制：只能在你填写的来源中出现的角色名，如：哈利波特`}
              {...register("roleName", roleNameRules())}
              bg={"bg.muted"}
              aria-invalid={!!errors.roleName}
            />
          </Field>

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

          <Center w={"full"}>
            <Button
              rounded={"full"}
              disabled={!canSubmitGenerate}
              loading={isSubmitting}
              variant={"outline"}
              onClick={handleSubmit(onGenerate)}
            >
              角色生成
            </Button>
          </Center>
        </Container>

        {/* 额外信息子表单（IP 形态） */}
        <Container
          maxW="800px"
          w={"full"}
          bg={"bg.default"}
          spaceY={6}
          borderRadius={"md"}
          padding={4}
          boxShadow="sm"
        >
          <ExtraInfoForm mode="ip" />

          <Center w={"full"}>
            <Button
              rounded={"full"}
              disabled={!canSubmitCreate}
              loading={isSubmitting}
              variant={"outline"}
              onClick={handleSubmit(onCreateAgent)}
            >
              创建智能体
            </Button>
          </Center>
        </Container>
      </Flex>
    </Flex>
  )
}
