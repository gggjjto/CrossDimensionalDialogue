import { Box } from "@chakra-ui/react"
import Masonry, { ResponsiveMasonry } from "react-responsive-masonry"
import InfiniteScroll from "react-infinite-scroll-component"

export interface MasonryGridProps<T = any> {
  /** 数据 */
  items: T[]
  /** 获取唯一标识 */
  getKey: (item: T, index: number) => string | number
  /** 渲染组件 */
  render: (item: T, index: number) => React.ReactNode
  /** 列数 */
  columns?: number | { [breakpoint: number]: number }
  /** 间距 */
  gutter?: string
  /** 是否还有更多数据 */
  hasMore: boolean
  /** 触发加载更多 */
  onLoadMore: () => void
  /** 自定义加载中提示 */
  loader?: React.ReactNode
  /** 自定义结束提示 */
  endMessage?: React.ReactNode
  /** 滚动容器 ID（非 window 滚动时需要） */
  scrollableTarget?: string
}

/**
 * 瀑布流组件，支持无限滚动
 */
export default function MasonryGrid<T>(props: MasonryGridProps<T>) {
  const {
    items,
    getKey,
    render,
    columns = { 350: 2, 700: 3, 1100: 4 },
    gutter = "16px",
    hasMore,
    onLoadMore,
    loader,
    endMessage,
    scrollableTarget,
  } = props

  return (
    <InfiniteScroll
      dataLength={items.length}
      next={onLoadMore}
      hasMore={hasMore}
      loader={loader}
      endMessage={endMessage}
      scrollableTarget={scrollableTarget}
      // 使用内联样式禁用默认容器的 overflow，避免影响外层布局
      style={{ overflow: "visible" }}
    >
      <ResponsiveMasonry columnsCountBreakPoints={columns as any}>
        <Masonry gutter={gutter}>
          {items.map((item, index) => (
            <Box key={getKey(item, index)}>{render(item, index)}</Box>
          ))}
        </Masonry>
      </ResponsiveMasonry>
    </InfiniteScroll>
  )
}
