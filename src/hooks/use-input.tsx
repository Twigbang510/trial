
import {Dispatch, SetStateAction, useCallback, useState} from 'react'
import validateHelper from 'validate.js'

export interface ValidationErrors {
  [key: string]: string[]
}

export interface Rules extends Record<string, any> {}

interface ValidationOptions {
  rules: Rules
}

interface InputOptions {
  hasPagination: boolean
  realtimeCheckError?: boolean
}

export function useInput<T extends Record<string, any>>(
  initialState: T = {} as T,
  validationOptions?: ValidationOptions,
  option?: InputOptions
): [
  T,
  Dispatch<SetStateAction<Partial<T> | undefined>>,
  {
    validation: { getErrors: any; errors: any; setErrors: any }
    resetInput: any
    trimSpaces: any
    trimSpacesOnChange: any
  }
] {
  const { hasPagination = false, realtimeCheckError = false } = option || {}

  const [inputs, setInputsLocal] = useState<T>(initialState)
  const [errors, setErrors] = useState<ValidationErrors>()

  const handleInputChange = useCallback(
    (data: Record<string, any> = {}) => {
      if (hasPagination && !data.page && !data.limit && !inputs.limit) {
        data.page = 1
        data.limit = 30
      }
      let newInput = null
      setInputsLocal((i) => {
        newInput = { ...i, ...data }
        return newInput
      })
      setInputsLocal((i) => ({ ...i, ...data }))

      if (realtimeCheckError && newInput) {
        getErrors(newInput)
      }
    },
    // eslint-disable-next-line
    [inputs.limit, hasPagination]
  )

  const resetInput = useCallback(() => {
    setInputsLocal(initialState)
  }, [initialState])

  const trimSpaces = (text?: string) => {
    if (!text) {
      return ''
    }
    return text.replace(/^\s+|\s+$/g, '').replace(/\s+/g, ' ')
  }

  const trimSpacesOnChange = (text?: string) => {
    if (!text) {
      return ''
    }
    return text.replace(/^\s+|\s+$/g, ' ').replace(/\s+/g, ' ')
  }

  const getErrors = (data?: T | null): ValidationErrors | undefined => {
    const rules = validationOptions?.rules
    if (!rules) {
      return undefined
    }
    validateHelper.validators.presence.options = { allowEmpty: false }
    validateHelper.validators.optional = (value: any, options: any) => {
      return !['', null, undefined].includes(value) ? validateHelper.single(value, options) : null
    }
    const validationErrors = validateHelper.validate(data || inputs, rules)
    setErrors(validationErrors)
    return validationErrors
  }

  return [
    inputs,
    handleInputChange,
    {
      validation: {
        getErrors,
        errors,
        setErrors
      },
      resetInput,
      trimSpaces,
      trimSpacesOnChange
    }
  ]
}
