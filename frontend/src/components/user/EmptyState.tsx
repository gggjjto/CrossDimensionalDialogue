import { Box, Stack, Text } from "@chakra-ui/react"
import { Link as RouterLink } from "@tanstack/react-router"

interface EmptyStateProps {
  title: string
  subtitle: string
  actionText?: string
  actionLink?: string
}

export default function EmptyState({ title, subtitle, actionText, actionLink }: EmptyStateProps) {
  return (
    <Box
      display="flex"
      alignItems="center"
      justifyContent="center"
      minH="400px"
      textAlign="center"
    >
      <Stack gap={4}>
        {/* 主标题 */}
        <Text fontSize="25px" color="fg.default" fontWeight="bold">
          {title} 
        </Text>
        {/* 副标题 */}
        <Text fontSize="30px" color="fg.muted">
          {subtitle}
        </Text>
        {/* 操作按钮 */}
        {actionText && actionLink && (
          <RouterLink
            to={actionLink}
            style={{
              color: "var(--chakra-colors-info-default)",
              fontSize: "15px",
              fontWeight: "500",
              textDecoration: "none"
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.textDecoration = "underline"
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.textDecoration = "none"
            }}
          >
            {actionText}
          </RouterLink>
        )}
      </Stack>
    </Box>
  )
}
