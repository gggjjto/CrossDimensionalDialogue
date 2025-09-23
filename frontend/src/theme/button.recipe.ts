import { defineRecipe } from "@chakra-ui/react"

// 按钮采用 zinc 中性灰主题，提供 primary / secondary / ghost 三种变体
export const buttonRecipe = defineRecipe({
  base: {
    fontWeight: "600",
    display: "inline-flex",
    alignItems: "center",
    justifyContent: "center",
    gap: "2",
    borderRadius: "md",
    transitionProperty: "common",
    transitionDuration: "base",
    _focusVisible: {
      outline: "2px solid",
      outlineColor: "accent.default",
      boxShadow: "0 0 0 4px {colors.focus.ring}",
    },
    _disabled: { opacity: 0.5, pointerEvents: "none" },
  },
  variants: {
    variant: {
      primary: {
        bg: "accent.default",
        color: "accent.foreground",
        _hover: { bg: "accent.emphasis" },
        _active: { bg: "zinc.900" },
      },
      secondary: {
        bg: "surface.default",
        color: "fg.default",
        borderWidth: "1px",
        borderColor: "border.default",
        _hover: { bg: "bg.muted" },
        _active: { bg: "zinc.100", _dark: { bg: "zinc.800" } },
      },
      ghost: {
        bg: "transparent",
        color: "fg.default",
        _hover: { bg: "bg.muted" },
      },
    },
    size: {
      md: { h: "10", px: "5", fontSize: "md" },
      lg: { h: "11", px: "6", fontSize: "md" },
    },
  },
  defaultVariants: { variant: "primary", size: "md" },
})
