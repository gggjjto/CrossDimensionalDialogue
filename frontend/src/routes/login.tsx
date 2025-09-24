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
import { FiMail } from "react-icons/fi"
import { LuArrowRight } from "react-icons/lu"

import { Button } from "@/components/ui/button"
import { InputGroup } from "@/components/ui/input-group"
import { PasswordInput } from "@/components/ui/password-input"
import useAuth, { isLoggedIn } from "@/hooks/useAuth"
import { emailPattern, passwordRules } from "../utils/rules"

export const Route = createFileRoute("/login")({
  component: Login,
  beforeLoad: async () => {
    // 如果用户已经登录，重定向到首页
    if (isLoggedIn()) {
      throw redirect({
        to: "/",
      })
    }
  },
})

// 登录表单数据类型
interface LoginFormData {
  email: string
  password: string
}

function Login() {
  const { loginMutation, error, resetError } = useAuth()
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginFormData>({
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues: {
      email: "",
      password: "",
    },
  })

  const onSubmit: SubmitHandler<LoginFormData> = async (data) => {
    if (isSubmitting) return

    resetError()

    try {
      await loginMutation.mutateAsync(data)
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
          <Card.Title>欢迎回来</Card.Title>
          <Card.Description>输入您的邮箱地址开始使用</Card.Description>
        </Card.Header>
        <Card.Body>
          <Stack gap="4" w="full">
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
                    (error ? "登录失败，请检查邮箱和密码" : "")}
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
          </Stack>
        </Card.Body>
        <Card.Footer flexDirection={"column"} gap={2}>
          <Button
            w={"full"}
            variant="solid"
            type="submit"
            loading={loginMutation.isPending}
            loadingText="登录中..."
          >
            登录 <LuArrowRight style={{ marginLeft: 4 }} />
          </Button>

          <Box
            backgroundColor="bg.muted"
            h="2px"
            margin={" 12px 0 5px 0"}
            w="full"
          ></Box>

          <Text color={"fg.muted"}>
            首次使用？点击
            <RouterLink to="/signup">
              {" "}
              <Text fontWeight={"bold"} display={"inline-block"}>
                创建账户
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
