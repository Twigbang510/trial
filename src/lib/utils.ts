import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export async function sleep(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

export const isJsonString = (str: string): boolean => {
  try {
    JSON.parse(str);
    return true;
  } catch {
    return false;
  }
};

export const convertSecondToMinute = (seconds:number):string => {
  const minutes = Math.floor(seconds / 60);
  const resSecond = Math.ceil(seconds % 60);
  const paddedSeconds = resSecond.toString().padStart(2, '0');
  return `${minutes}:${paddedSeconds}`;
}