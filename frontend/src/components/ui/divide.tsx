import { Box, type BoxProps } from "@chakra-ui/react"
import { forwardRef } from "react"

export interface DivideProps extends Omit<BoxProps, "color"> {
  /** 方向 */
  orientation?: "horizontal" | "vertical"
  /** 厚度 */
  thickness?: string | number
  /** 颜色 */
  color?: BoxProps["borderColor"]
  /** 样式 */
  variant?: "solid" | "dashed" | "dotted"
  /** 长度 */
  length?: string | number
}

/**
 * 分割线
 */
export const Divide = forwardRef<HTMLDivElement, DivideProps>(function Divide(
  props,
  ref
) {
  const {
    orientation = "horizontal",
    thickness = "1px",
    color = "border.default",
    variant = "solid",
    length,
    ...rest
  } = props

  const isHorizontal = orientation === "horizontal"

  const sizeProps = isHorizontal
    ? { width: length ?? "100%", height: 0 }
    : { height: length ?? "100%", width: 0 }

  const borderProps = isHorizontal
    ? { borderTopWidth: thickness, borderTopStyle: variant, borderColor: color }
    : {
        borderInlineStartWidth: thickness,
        borderInlineStartStyle: variant,
        borderColor: color,
      }

  return (
    <Box
      ref={ref}
      role="separator"
      aria-orientation={orientation}
      {...sizeProps}
      {...borderProps}
      {...rest}
    />
  )
})

export default Divide
