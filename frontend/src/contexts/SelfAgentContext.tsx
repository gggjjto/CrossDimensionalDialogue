import { createContext, useContext, useReducer, ReactNode } from "react"
import { SelfForm } from "../components/create-agent/SelfFormPage"
import { ExtraInfoValues } from "../components/create-agent/ExtraInfoForm"

export type AgentMode = "self" | "ip"

export interface IpForm {
  ipSource: string
  roleName: string
  style: "" | "real" | "anime"
}

// 状态接口
interface SelfAgentState {
  // 模式：self 或 ip
  mode: AgentMode
  // 表单数据
  selfFormData: SelfForm
  ipFormData: IpForm
  extraData: ExtraInfoValues
  isExtraFormValid: boolean

  // 图片数据
  generatedImages: string[]
  selectedImage?: string
  createdCharacterId?: string

  // UI 状态
  isGenerating: boolean
  isCreating: boolean
}

// 初始状态
const initialState: SelfAgentState = {
  mode: "self",
  selfFormData: {
    style: "",
    description: "",
  },
  ipFormData: {
    ipSource: "",
    roleName: "",
    style: "",
  },
  extraData: {
    relationWithUser: "",
    publicInfo: "",
    openingLine: "",
  },
  isExtraFormValid: false,
  generatedImages: [],
  selectedImage: undefined,
  createdCharacterId: undefined,
  isGenerating: false,
  isCreating: false,
}

// Action 类型
type SelfAgentAction =
  | { type: "SET_MODE"; payload: AgentMode }
  | { type: "SET_SELF_FORM"; payload: SelfForm }
  | { type: "SET_IP_FORM"; payload: IpForm }
  | { type: "SET_EXTRA_DATA"; payload: ExtraInfoValues }
  | { type: "SET_EXTRA_FORM_VALID"; payload: boolean }
  | { type: "SET_GENERATED_IMAGES"; payload: string[] }
  | { type: "SET_SELECTED_IMAGE"; payload?: string }
  | { type: "SET_GENERATING"; payload: boolean }
  | { type: "SET_CREATING"; payload: boolean }
  | { type: "SET_CREATED_CHARACTER_ID"; payload?: string }
  | { type: "RESET_STATE" }

// Reducer
function selfAgentReducer(
  state: SelfAgentState,
  action: SelfAgentAction
): SelfAgentState {
  switch (action.type) {
    case "SET_MODE":
      return { ...state, mode: action.payload }
    case "SET_SELF_FORM":
      return { ...state, selfFormData: action.payload }
    case "SET_IP_FORM":
      return { ...state, ipFormData: action.payload }
    case "SET_EXTRA_DATA":
      return { ...state, extraData: action.payload }
    case "SET_EXTRA_FORM_VALID":
      return { ...state, isExtraFormValid: action.payload }
    case "SET_GENERATED_IMAGES":
      return { ...state, generatedImages: action.payload, selectedImage: action.payload?.[0] }
    case "SET_SELECTED_IMAGE":
      return { ...state, selectedImage: action.payload }
    case "SET_CREATED_CHARACTER_ID":
      return { ...state, createdCharacterId: action.payload }
    case "SET_GENERATING":
      return { ...state, isGenerating: action.payload }
    case "SET_CREATING":
      return { ...state, isCreating: action.payload }
    case "RESET_STATE":
      return initialState
    default:
      return state
  }
}

// Context 接口
interface SelfAgentContextType {
  state: SelfAgentState
  dispatch: React.Dispatch<SelfAgentAction>
}

// 创建 Context
const SelfAgentContext = createContext<SelfAgentContextType | undefined>(
  undefined
)

// Provider 组件
interface SelfAgentProviderProps {
  children: ReactNode
}

export function SelfAgentProvider({ children }: SelfAgentProviderProps) {
  const [state, dispatch] = useReducer(selfAgentReducer, initialState)

  const contextValue: SelfAgentContextType = {
    state,
    dispatch,
  }

  return (
    <SelfAgentContext.Provider value={contextValue}>
      {children}
    </SelfAgentContext.Provider>
  )
}

// Hook
export function useSelfAgent() {
  const context = useContext(SelfAgentContext)
  if (context === undefined) {
    throw new Error("useSelfAgent must be used within a SelfAgentProvider")
  }
  return context
}
