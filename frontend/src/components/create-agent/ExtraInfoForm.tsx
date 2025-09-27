import { Field } from "@/components/ui/field"
import { Box, Input, Textarea } from "@chakra-ui/react"
import { useEffect, useMemo } from "react"
import { useForm } from "react-hook-form"
import {
  bioRules,
  nicknameRules,
  settingRules,
  relationWithUserRules,
  publicInfoRules,
  openingLineRules,
} from "@/utils/rules"
import { useSelfAgent } from "@/contexts/SelfAgentContext"

export type ExtraFormMode = "ip" | "self"

export interface ExtraInfoValues {
  // self 模式新增
  nickname?: string
  biography?: string
  setting?: string
  relationWithUser: string
  publicInfo: string
  openingLine: string
}

interface ExtraInfoFormProps {
  mode?: ExtraFormMode
}

export default function ExtraInfoForm(props: ExtraInfoFormProps) {
  const { mode = "ip" } = props
  const { state, dispatch } = useSelfAgent()

  const {
    register,
    watch,
    formState: { errors, isValid },
    reset,
  } = useForm<ExtraInfoValues>({
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues: state.extraData,
  })

  const rawValues = watch()

  // 使用 useMemo 来稳定 values 对象引用
  const values = useMemo(
    () => rawValues as ExtraInfoValues,
    [
      rawValues.nickname,
      rawValues.biography,
      rawValues.setting,
      rawValues.relationWithUser,
      rawValues.publicInfo,
      rawValues.openingLine,
    ]
  )

  // 更新 Context 状态
  useEffect(() => {
    dispatch({ type: "SET_EXTRA_DATA", payload: values })
    dispatch({ type: "SET_EXTRA_FORM_VALID", payload: isValid })
  }, [values, isValid, dispatch])

  // 当外部的 extraData（来自生成设定的写入）变化时，重置表单以回填到输入框
  useEffect(() => {
    reset(state.extraData)
  }, [state.extraData, reset])

  return (
    <Box w={"full"} spaceY={6}>
      {mode === "self" && (
        <>
          <Field
            label="昵称"
            required
            invalid={!!errors.nickname}
            errorText={errors.nickname?.message}
          >
            <Input
              {...register("nickname", nicknameRules(true))}
              placeholder="请输入角色名称"
              bg={"bg.muted"}
            />
          </Field>

          <Field
            label="生平简述"
            invalid={!!errors.biography}
            errorText={errors.biography?.message}
          >
            <Textarea
              {...register("biography", bioRules(false))}
              placeholder="请描述角色身份"
              bg={"bg.muted"}
              minH={28}
            />
          </Field>

          <Field
            label="设定"
            required
            invalid={!!errors.setting}
            errorText={errors.setting?.message}
          >
            <Textarea
              {...register("setting", settingRules(true))}
              placeholder={
                "请描述你想要的智能体性格及聊天风格，例如：开朗外向、幽默风趣；聊天风格：语言活泼、用词直白、句式短句多等"
              }
              bg={"bg.muted"}
              minH={28}
            />
          </Field>
        </>
      )}
      <Field
        label="与角色的关系（选填）"
        invalid={!!errors.relationWithUser}
        errorText={errors.relationWithUser?.message}
      >
        <Textarea
          {...register("relationWithUser", relationWithUserRules(false))}
          placeholder="请描述用户与角色的关系，如：用户是霍格沃茨魔法学校的新生，哈利波特的学弟/学妹"
          bg={"bg.muted"}
          minH={28}
        />
      </Field>

      <Field
        label="对外展示（选填）"
        invalid={!!errors.publicInfo}
        errorText={errors.publicInfo?.message}
      >
        <Textarea
          {...register("publicInfo", publicInfoRules(false))}
          placeholder="在此输入作者想说明的话及角色对外的能被他人了解的信息，如背景、身份、与用户的关系等"
          bg={"bg.muted"}
          minH={28}
        />
      </Field>

      <Field
        label="开场白"
        invalid={!!errors.openingLine}
        errorText={errors.openingLine?.message}
      >
        <Textarea
          {...register("openingLine", openingLineRules(true))}
          placeholder="作为角色所说的一句话，可用（）来描述动作或场景"
          bg={"bg.muted"}
          minH={24}
        />
      </Field>
    </Box>
  )
}
