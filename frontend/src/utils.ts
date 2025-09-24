export const emailPattern = {
  value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
  message: "Invalid email address",
}

export const namePattern = {
  value: /^[A-Za-z\s\u00C0-\u017F]{1,30}$/,
  message: "Invalid name",
}

export const passwordRules = (isRequired = true) => {
  const rules: any = {
    minLength: {
      value: 8,
      message: "密码必须至少8个字符",
    },
  }

  if (isRequired) {
    rules.required = "密码是必填项"
  }

  return rules
}

export const confirmPasswordRules = (
  getValues: () => any,
  isRequired = true
) => {
  const rules: any = {
    validate: (value: string) => {
      const password = getValues().password || getValues().new_password
      return value === password ? true : "密码不匹配"
    },
  }

  if (isRequired) {
    rules.required = "请再次输入密码"
  }

  return rules
}
