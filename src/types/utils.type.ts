export interface SuccessResponse<Data> {
  message: string
  data: Data
}

export interface PayloadSuccessResponse<Data> {
  data: Data
  totalRecords: number,
  pageCount: number,
  page: number,
  pageSize: number,
  orderBy: [
    {
      id: string
    }
  ]
}

export interface ErrorResponse<Data> {
  message: string
  data?: Data
}

export type NoUndefinedField<T> = {
  [P in keyof T]-?: NoUndefinedField<NonNullable<T[P]>>
}

export type Nameable = {
  name?: string
  full_name?: string
}

export interface SelectOption {
  label: string
  value: number
}