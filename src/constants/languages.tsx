export interface Language {
  code: string;
  label: string;
  flag: string;
}

export const AVAILABLE_LANGUAGE: Language[] = [
  {
    code: "vi-north",
    label: "Tiếng Việt (Bắc)",
    flag: "/flags/vi-VN.svg",
  },
  {
    code: "vi-central",
    label: "Tiếng Việt (Trung)",
    flag: "/flags/vi-VN.svg",
  },
  {
    code: "vi-south",
    label: "Tiếng Việt (Nam)",
    flag: "/flags/vi-VN.svg",
  },
  { code: "en", label: "English", flag: "/flags/en-US.svg" }, // English
  { code: "zh", label: "中文", flag: "/flags/zh-CN.svg" }, // Chinese
  { code: "ja", label: "日本語", flag: "/flags/ja-JP.svg" }, // Japanese
  { code: "ko", label: "한국어", flag: "/flags/ko-KR.svg" }, // Korean
  { code: "th", label: "ไทย", flag: "/flags/th-TH.svg" }, // Thai
  { code: "ru", label: "Русский", flag: "/flags/ru-RU.svg" }, // Russian
  { code: "fr", label: "Français", flag: "/flags/fr-FR.svg" }, // French
  { code: "es", label: "Español", flag: "/flags/es-ES.svg" }, // Spanish
  { code: "hi", label: "हिन्दी", flag: "/flags/hi-IN.svg" }, // Hindi
  { code: "pt", label: "Português", flag: "/flags/pt-PT.svg" }, // Portuguese
  { code: "de", label: "Deutsch", flag: "/flags/de-DE.svg" }, // German
  { code: "fi", label: "Suomi", flag: "/flags/fi-FI.svg" }, // Finnish
  { code: "it", label: "Italiano", flag: "/flags/it-IT.svg" }, // Italian
  { code: "pl", label: "Polski", flag: "/flags/pl-PL.svg" }, // Polish
];
