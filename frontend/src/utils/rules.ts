// =====================
// Login & Signup 表单校验
// =====================

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

// =====================
// Create Agent 表单校验
// =====================

// 可与 react-hook-form 兼容的规则对象
export const ipSourceRules = (isRequired = true) => {
  const rules: any = {
    required: "请填写IP来源",
    minLength: { value: 2, message: "IP来源至少2个字符" },
  }

  if (isRequired) {
    rules.required = "请填写IP来源"
  }

  return rules
}

export const roleNameRules = (isRequired = true) => {
  const rules: any = {
    required: "请填写角色名称",
    minLength: { value: 1, message: "角色名称至少1个字符" },
    maxLength: { value: 50, message: "角色名称不超过50个字符" },
  }

  if (isRequired) {
    rules.required = "请填写角色名称"
  }

  return rules
}

export const styleRules = (isRequired = true) => {
  const rules: any = {
    required: "请选择风格",
  }

  if (isRequired) {
    rules.required = "请选择风格"
  }

  return rules
}

// =====================
// Extra Info 子表单（self 模式会新增）
// =====================

export const nicknameRules = (isRequired = true) => {
  const rules: any = {
    required: "请填写昵称",
    minLength: { value: 1, message: "昵称至少1个字符" },
    maxLength: { value: 30, message: "昵称不超过30个字符" },
  }

  if (!isRequired) {
    delete rules.required
  }

  return rules
}

export const bioRules = (isRequired = false) => {
  const rules: any = {}
  if (isRequired) {
    rules.required = "请填写生平简介"
  }
  return rules
}

export const settingRules = (isRequired = true) => {
  const rules: any = {
    required: "请填写设定",
    minLength: { value: 2, message: "设定至少2个字符" },
  }
  if (!isRequired) {
    delete rules.required
  }
  return rules
}

export const relationWithUserRules = (isRequired = false) => {
  const rules: any = {}
  if (isRequired) {
    rules.required = "请填写与角色的关系"
  }
  return rules
}

export const publicInfoRules = (isRequired = false) => {
  const rules: any = {}
  if (isRequired) {
    rules.required = "请填写对外展示"
  }
  return rules
}

export const openingLineRules = (isRequired = true) => {
  const rules: any = {
    required: "请填写开场白",
    minLength: { value: 1, message: "开场白至少1个字符" },
    maxLength: { value: 100, message: "开场白不超过100个字符" },
  }
  if (!isRequired) {
    delete rules.required
  }
  return rules
}
