import { useInfiniteQuery } from "@tanstack/react-query"
import { charactersApi } from "@/api/characters"
import type { CharacterPublic } from "@/api/characters/type"

export const useAgentList = (search?: string) => {
  const limit = 20

  // 使用 useInfiniteQuery 处理分页数据
  const {
    data,
    isLoading,
    isFetchingNextPage,
    hasNextPage,
    fetchNextPage,
    refetch,
  } = useInfiniteQuery({
    queryKey: ["agentList", search], // 搜索关键词变化时重新查询
    queryFn: async ({ pageParam = 0 }) => {
      if (search && search.trim()) {
        // 搜索模式
        const res = await charactersApi.search(search.trim(), {
          offset: pageParam,
          limit,
        })
        // 转换搜索结果到角色列表（接口返回 results 数组，包含 character 字段）
        const list = (res.results || [])
          .map((r: any) => r.character)
          .filter(Boolean) as CharacterPublic[]

        return {
          characters: list,
          total: res.total,
          hasMore: list.length === limit && pageParam + list.length < res.total,
        }
      } else {
        // 普通列表模式
        const res = await charactersApi.getPublicCharacters({
          skip: pageParam,
          limit,
        })
        return {
          characters: res.characters,
          total: res.total,
          hasMore:
            res.characters.length === limit &&
            pageParam + res.characters.length < res.total,
        }
      }
    },
    getNextPageParam: (lastPage, allPages) => {
      // 如果没有更多数据，返回 undefined
      if (!lastPage.hasMore) return undefined

      // 计算下一页的偏移量
      const totalLoaded = allPages.reduce(
        (sum, page) => sum + page.characters.length,
        0
      )
      return totalLoaded
    },
    initialPageParam: 0,
    select: (data) => data.pages.flatMap((page) => page.characters),
  })

  // 加载更多数据
  const loadMore = () => {
    if (hasNextPage && !isFetchingNextPage) {
      fetchNextPage()
    }
  }

  // 刷新数据
  const refresh = () => {
    refetch()
  }

  return {
    // 数据
    characters: data,

    // 状态
    isLoading,
    hasMore: hasNextPage,
    isFetchingNextPage,

    // 操作
    loadMore,
    refresh,
  }
}
