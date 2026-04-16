// Google Identity Services types
declare global {
  interface Window {
    google?: {
      accounts: {
        id: {
          initialize: (config: {
            client_id: string;
            callback: (response: { credential: string }) => void;
          }) => void;
          prompt: () => void;
        };
      };
    };
    FB?: {
      init: (config: { appId: string; version: string; xfbml?: boolean }) => void;
      login: (
        callback: (response: { authResponse?: { accessToken: string }; status: string }) => void,
        options?: {
          scope?: string;
          width?: number;
          height?: number;
          left?: number;
          top?: number;
        }
      ) => void;
    };
    fbAsyncInit?: () => void;
  }
}

export {};