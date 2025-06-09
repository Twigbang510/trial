const set = (key: string, data: unknown) => {
  if (typeof window !== "undefined") {
    if (!window.localStorage || !window.JSON || !key) {
      return;
    }

    if (typeof data === "object") {
      window.localStorage.setItem(key, JSON.stringify(data));
    } else if (["string", "number"].includes(typeof data)) {
      window.localStorage.setItem(key, data as string);
    }
  }
};

const get = (key: string) => {
  if (typeof window !== "undefined") {
    if (!window.localStorage || !window.JSON || !key) {
      return;
    }
    const item = window.localStorage.getItem(key);

    if (!item || item === "undefined") {
      return;
    }

    try {
      return JSON.parse(item);
    } catch {
      return item;
    }
  }
};

const remove = (key: string) => {
  if (typeof window !== "undefined") {
    if (!window.localStorage || !window.JSON || !key) {
      return;
    }
    window.localStorage.removeItem(key);
  }
};

const clear = () => {
  if (typeof window !== "undefined") {
    if (!window.localStorage || !window.JSON) {
      return;
    }
    window.localStorage.clear();
  }
};

export const LocalStorage = {
  set,
  get,
  remove,
  clear,
};
