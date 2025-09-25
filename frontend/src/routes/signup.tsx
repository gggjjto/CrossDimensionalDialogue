import {
  Box,
  Card,
  Container,
  Field,
  Input,
  Link,
  Stack,
  Text,
} from "@chakra-ui/react"
import {
  createFileRoute,
  Link as RouterLink,
  redirect,
} from "@tanstack/react-router"
import { type SubmitHandler, useForm } from "react-hook-form"
import { FiMail, FiUser } from "react-icons/fi"
import { LuArrowRight } from "react-icons/lu"

import { Button } from "@/components/ui/button"
import { InputGroup } from "@/components/ui/input-group"
import { PasswordInput } from "@/components/ui/password-input"
import useAuth, { isLoggedIn } from "@/hooks/useAuth"
import {
  confirmPasswordRules,
  emailPattern,
  passwordRules,
} from "@/utils/rules"
// Logo removed as unused

export const Route = createFileRoute("/signup")({
  component: SignUp,
  beforeLoad: async () => {
    if (isLoggedIn()) {
      throw redirect({
        to: "/",
      })
    }
  },
})

interface UserRegisterForm {
  email: string
  full_name: string
  password: string
  confirm_password: string
}

function SignUp() {
  const { registerMutation, error, resetError } = useAuth()
  const {
    register,
    handleSubmit,
    getValues,
    formState: { errors, isSubmitting },
  } = useForm<UserRegisterForm>({
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues: {
      email: "",
      full_name: "",
      password: "",
      confirm_password: "",
    },
  })

  const onSubmit: SubmitHandler<UserRegisterForm> = async (data) => {
    if (isSubmitting) return

    resetError()

    try {
      await registerMutation.mutateAsync({
        email: data.email,
        password: data.password,
        full_name: data.full_name,
      })
    } catch {
      // 错误由 useAuth hook 处理
    }
  }

  return (
    <Container
      as="form"
      onSubmit={handleSubmit(onSubmit)}
      h="100vh"
      alignItems="stretch"
      justifyContent="center"
      gap={4}
      centerContent
      maxW={"lg"}
    >
      <Box textAlign="center" fontSize="lg" mb={4} className="text-muted">
        创建属于你的AI角色
      </Box>

      <Card.Root maxW={"lg"} variant={"elevated"}>
        <Card.Header alignItems="center" mb={4}>
          <Card.Title>创建账户</Card.Title>
          <Card.Description>输入您的信息开始使用</Card.Description>
        </Card.Header>
        <Card.Body>
          <Stack gap="4" w="full">
            <Field.Root invalid={!!errors.full_name}>
              <Field.Label>昵称</Field.Label>
              <InputGroup w="100%" startElement={<FiUser />}>
                <Input
                  minLength={3}
                  {...register("full_name", {
                    required: "姓名为必填项",
                  })}
                  placeholder="请输入您的姓名"
                  type="text"
                />
              </InputGroup>
              {errors.full_name && (
                <Field.ErrorText>{errors.full_name.message}</Field.ErrorText>
              )}
            </Field.Root>

            <Field.Root invalid={!!errors.email || !!error}>
              <Field.Label>邮箱地址</Field.Label>
              <InputGroup startElement={<FiMail />} w="full">
                <Input
                  {...register("email", {
                    required: "邮箱地址是必填项",
                    pattern: emailPattern,
                  })}
                  placeholder="请输入您的邮箱地址"
                  type="email"
                />
              </InputGroup>
              {(errors.email || error) && (
                <Field.ErrorText>
                  {errors.email?.message ||
                    (error ? "注册失败，请检查信息" : "")}
                </Field.ErrorText>
              )}
            </Field.Root>

            <Field.Root invalid={!!errors.password}>
              <Field.Label>密码</Field.Label>
              <PasswordInput
                {...register("password", passwordRules())}
                type="password"
                placeholder="请输入密码"
                errors={errors}
              />
            </Field.Root>

            <Field.Root invalid={!!errors.confirm_password}>
              <Field.Label>确认密码</Field.Label>
              <PasswordInput
                {...register(
                  "confirm_password",
                  confirmPasswordRules(getValues)
                )}
                type="confirm_password"
                placeholder="请再次输入密码"
                errors={errors}
              />
            </Field.Root>
          </Stack>
        </Card.Body>
        <Card.Footer flexDirection={"column"} gap={2}>
          <Button
            w={"full"}
            variant="solid"
            type="submit"
            loading={registerMutation.isPending}
            loadingText="创建中..."
          >
            创建账户 <LuArrowRight style={{ marginLeft: 4 }} />
          </Button>

          <Box
            backgroundColor="bg.muted"
            h="2px"
            margin={" 12px 0 5px 0"}
            w="full"
          ></Box>

          <Text color={"fg.muted"}>
            已有账户？点击
            <RouterLink to="/login">
              {" "}
              <Text fontWeight={"bold"} display={"inline-block"}>
                登录
              </Text>
            </RouterLink>
          </Text>
        </Card.Footer>
      </Card.Root>

      <Box textAlign={"center"}>
        使用AI智能体即代表您同意我们的{" "}
        <Link href="/" display={"inline-block"} fontWeight={"bold"}>
          服务条款
        </Link>{" "}
        和{" "}
        <Link href="/" display={"inline-block"} fontWeight={"bold"}>
          隐私政策
        </Link>
      </Box>
    </Container>
  )
}

export default SignUp
