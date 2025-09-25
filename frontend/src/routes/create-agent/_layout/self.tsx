import { Box } from "@chakra-ui/react"
import { createFileRoute } from "@tanstack/react-router"
import { Swiper, SwiperSlide } from "swiper/react"
import { Navigation, Pagination } from "swiper/modules"
import { HiChevronLeft, HiChevronRight } from "react-icons/hi2"
import { useEffect } from "react"

// 导入 Swiper 样式
import "swiper/css"
import "swiper/css/navigation"
import "swiper/css/pagination"

import SelfFormPage from "@/components/create-agent/SelfFormPage"
import SelfExtraInfoPage from "@/components/create-agent/SelfExtraInfoPage"
import { useSelfAgent } from "@/contexts/SelfAgentContext"

export const Route = createFileRoute("/create-agent/_layout/self")({
  component: RouteComponent,
})

function RouteComponent() {
  return <SelfAgentContent />
}

function SelfAgentContent() {
  const { dispatch } = useSelfAgent()

  useEffect(() => {
    dispatch({ type: "SET_MODE", payload: "self" })
  }, [dispatch])

  return (
    <Box h={"90%"} w={"full"}>
      <Swiper
        modules={[Navigation, Pagination]}
        spaceBetween={50}
        slidesPerView={1}
        navigation={{
          nextEl: ".swiper-button-next",
          prevEl: ".swiper-button-prev",
        }}
        pagination={{
          clickable: true,
          bulletClass: "swiper-pagination-bullet",
          bulletActiveClass: "swiper-pagination-bullet-active",
        }}
        className="mySwiper"
        style={{ height: "100%", width: "100%" }}
      >
        {/* 第一页：表单和预览区域 */}
        <SwiperSlide>
          <SelfFormPage />
        </SwiperSlide>

        {/* 第二页：ExtraInfoForm 表单 */}
        <SwiperSlide>
          <SelfExtraInfoPage />
        </SwiperSlide>

        {/* 自定义导航按钮 */}
        <Box
          className="swiper-button-prev"
          position={"absolute"}
          left={4}
          top={"50%"}
          transform={"translateY(-50%)"}
          zIndex={10}
          cursor={"pointer"}
          bg={"white"}
          borderRadius={"full"}
          p={2}
          boxShadow={"md"}
          _hover={{ bg: "gray.50" }}
        >
          <HiChevronLeft size={36} color={"#71717a"} />
        </Box>

        <Box
          className="swiper-button-next"
          position={"absolute"}
          right={4}
          top={"50%"}
          transform={"translateY(-50%)"}
          zIndex={10}
          cursor={"pointer"}
          bg={"white"}
          borderRadius={"full"}
          p={2}
          boxShadow={"md"}
          _hover={{ bg: "gray.50" }}
        >
          <HiChevronRight size={36} color={"#71717a"} />
        </Box>
      </Swiper>
    </Box>
  )
}
