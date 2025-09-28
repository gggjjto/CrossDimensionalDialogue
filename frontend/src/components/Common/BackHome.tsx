import { Box, Button, IconButton } from "@chakra-ui/react"
import { useNavigate } from "@tanstack/react-router"
import { HiOutlineHome } from "react-icons/hi"

type BackHomeButtonProps = {
  label?: string
  variant?: "ghost" | "solid" | "outline"
  size?: "xs" | "sm" | "md" | "lg"
  iconOnly?: boolean
  position?: "static" | "relative" | "absolute" | "fixed" | "sticky"
  top?: string | number
  left?: string | number
  right?: string | number
  bottom?: string | number
  zIndex?: number | string
}

export default function BackHomeButton(props: BackHomeButtonProps) {
  const navigate = useNavigate()
  const {
    label = "返回首页",
    variant = "ghost",
    size = "sm",
    iconOnly = true,
    position = "absolute",
    top = "4",
    left = "4",
    right,
    bottom, 
    zIndex = 10,
  } = props

  const common = {
    variant,
    size,
    onClick: () => navigate({ to: "/" }),
    borderRadius: "md",
    ...(variant === "ghost"
      ? { bg: "rgba(0,0,0,0.3)", _hover: { bg: "rgba(0,0,0,0.5)" }, color: "white" }
      : {}),
  } as const

  return (
    <Box position={position} top={top} left={left} right={right} bottom={bottom} zIndex={zIndex}>
      {iconOnly ? (
        <IconButton aria-label={label} {...common}>
          <HiOutlineHome />
        </IconButton>
      ) : (
        <Button {...common}>
          <HiOutlineHome style={{ marginRight: 6 }} />
          {label}
        </Button>
      )}
    </Box>
  )
}


