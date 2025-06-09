import { useState } from "react";
import { AVAILABLE_LANGUAGE, Language } from "../constants/languages";
import clsx from "clsx";
import useGlobalStore from "@/store/useGlobalStore";

export default function LanguageDropdown() {
  const [selectedLang, setSelectedLang] = useState<Language>(
    AVAILABLE_LANGUAGE[1],
  );
  const { setSelectedLanguageCode } = useGlobalStore();

  const [open, setOpen] = useState(false);

  const handleSelect = (lang: Language) => {
    setSelectedLang(lang);
    setSelectedLanguageCode(lang.code);
    setOpen(false);
  };

  return (
    <div className="relative flex flex-col items-center z-50">
      <button
        onClick={() => setOpen((prev) => !prev)}
        className="w-8 h-8 rounded-full overflow-hidden shadow-md"
      >
        <img
          src={selectedLang?.flag}
          alt={selectedLang?.code}
          className="w-full h-full"
        />
      </button>

      {/* Overlay */}
      <div
        className={clsx(
          "fixed inset-0 z-40 transition-opacity duration-200",
          open
            ? "bg-black bg-opacity-0 pointer-events-auto"
            : "opacity-0 pointer-events-none",
        )}
        onClick={() => setOpen(false)}
      />

      {/* Dropdown always mounted */}
      <div
        className={clsx(
          "absolute top-12 right-0 py-2 min-w-40 max-h-[60svh] overflow-y-auto px-4 bg-white rounded-lg shadow-md border border-gray-200 z-50 transition-all duration-200",
          open
            ? "opacity-100 translate-y-0 pointer-events-auto"
            : "opacity-0 -translate-y-2 pointer-events-none",
        )}
      >
        {AVAILABLE_LANGUAGE.map((lang) => (
          <button
            key={lang.code}
            onClick={() => handleSelect(lang)}
            className="w-full h-10 hover:bg-gray-100 mb-2 flex items-center justify-start gap-2"
          >
            <img
              src={lang.flag}
              alt={lang.label}
              className="w-8 h-8 rounded-full"
            />
            <span
              className={clsx(
                "text-xs font-semibold flex items-center justify-center grow",
                selectedLang.code === lang.code && "text-primary",
              )}
            >
              {lang.label}
            </span>
          </button>
        ))}
      </div>
    </div>
  );
}
