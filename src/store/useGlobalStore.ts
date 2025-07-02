import { useState } from 'react';

interface GlobalState {
  language: string;
  setLanguage: (language: string) => void;
}

const useGlobalStore = (selector?: (state: GlobalState) => any) => {
  const [language, setLanguage] = useState('en');
  
  const state = {
    language,
    setLanguage,
  };
  
  return selector ? selector(state) : state;
};

export default useGlobalStore; 