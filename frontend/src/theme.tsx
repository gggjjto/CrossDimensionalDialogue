import { createSystem, defaultConfig } from "@chakra-ui/react"
import { buttonRecipe } from "./theme/button.recipe"

export const system = createSystem(defaultConfig, {
  globalCss: {
    html: {
      fontSize: "16px",
    },
    body: {
      fontSize: "0.875rem",
      margin: 0,
      padding: 0,
    },
    ".main-link": {
      color: "accent.default",
      fontWeight: "bold",
    },
    // 常用文本颜色快捷类
    ".text-muted": { color: "fg.muted" },
    ".text-accent": { color: "accent.default" },
    ".text-success": { color: "success" },
    ".text-warning": { color: "warning" },
    ".text-danger": { color: "danger" },
    ".text-info": { color: "info" },
  },
  theme: {
    tokens: {
      colors: {
        // shadcn/ui zinc 调色板
        zinc: {
          50: { value: "#fafafa" },
          100: { value: "#f4f4f5" },
          200: { value: "#e4e4e7" },
          300: { value: "#d4d4d8" },
          400: { value: "#a1a1aa" },
          500: { value: "#71717a" },
          600: { value: "#52525b" },
          700: { value: "#3f3f46" },
          800: { value: "#27272a" },
          900: { value: "#18181b" },
          950: { value: "#09090b" },
        },
        // 状态色，仅用于提示/校验
        success: { value: "#10B981" },
        warning: { value: "#F59E0B" },
        danger: { value: "#EF4444" },
        info: { value: "#3B82F6" },
      },
    },
    semanticTokens: {
      colors: {
        // 站点主色采用中性灰（zinc）
        accent: {
          default: { value: "{colors.zinc.800}" },
          emphasis: { value: "{colors.zinc.900}" },
          foreground: { value: "#ffffff" },
          primary: { value: "{colors.zinc.800}" },
          secondary: { value: "{colors.zinc.700}" },
          tertiary: { value: "{colors.zinc.600}" },
          quaternary: { value: "{colors.zinc.500}" },
          quinary: { value: "{colors.zinc.400}" },
          senary: { value: "{colors.zinc.300}" },
          septenary: { value: "{colors.zinc.200}" },
          octonary: { value: "{colors.zinc.100}" },
          nonary: { value: "{colors.zinc.50}" },
        },
        bg: {
          default: { value: { base: "#ffffff", _dark: "{colors.zinc.950}" } },
          muted: {
            value: { base: "{colors.zinc.50}", _dark: "{colors.zinc.900}" },
          },
          hover: {
            value: { base: "{colors.zinc.100}", _dark: "{colors.zinc.800}" },
          },
          active: {
            value: { base: "{colors.zinc.200}", _dark: "{colors.zinc.700}" },
          },
        },
        surface: {
          default: { value: { base: "#ffffff", _dark: "{colors.zinc.900}" } },
          elevated: { value: { base: "#ffffff", _dark: "{colors.zinc.800}" } },
        },
        fg: {
          default: {
            value: { base: "{colors.zinc.900}", _dark: "{colors.zinc.100}" },
          },
          muted: {
            value: { base: "{colors.zinc.600}", _dark: "{colors.zinc.400}" },
          },
        },
        border: {
          default: {
            value: { base: "{colors.zinc.200}", _dark: "{colors.zinc.800}" },
          },
          muted: {
            value: { base: "{colors.zinc.300}", _dark: "{colors.zinc.700}" },
          },
        },
        // 状态语义色
        success: {
          default: { value: "{colors.success}" },
          foreground: { value: "#ffffff" },
        },
        warning: {
          default: { value: "{colors.warning}" },
          foreground: { value: "{colors.zinc.950}" },
        },
        danger: {
          default: { value: "{colors.danger}" },
          foreground: { value: "#ffffff" },
        },
        info: {
          default: { value: "{colors.info}" },
          foreground: { value: "#ffffff" },
        },
        // 统一的 focus ring（灰色半透明）
        focus: {
          ring: {
            value: {
              base: "rgba(24,24,27,.14)",
              _dark: "rgba(250,250,250,.20)",
            },
          },
        },
      },
    },
    recipes: {
      button: buttonRecipe,
    },
    // 文本样式：在 Text/Heading 等组件上可通过 textStyle 使用
    textStyles: {
      body: { color: "fg.default" },
      muted: { color: "fg.muted" },
      accent: { color: "accent.default" },
      success: { color: "success" },
      warning: { color: "warning" },
      danger: { color: "danger" },
      info: { color: "info" },
    },
  },
})
