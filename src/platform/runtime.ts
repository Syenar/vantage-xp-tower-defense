export type RuntimeKind = 'web' | 'cordova';

declare global {
  interface Window {
    __CORDOVA_BUILD__?: boolean;
    cordova?: { platformId?: string };
  }
}

export interface PlatformRuntime {
  kind: RuntimeKind;
  platformId: string;
  isNativeShell: boolean;
}

function waitForCordovaReady(): Promise<void> {
  return new Promise((resolve) => {
    document.addEventListener('deviceready', () => resolve(), { once: true });
  });
}

export async function initializePlatformRuntime(): Promise<PlatformRuntime> {
  if (!window.__CORDOVA_BUILD__) {
    return { kind: 'web', platformId: 'browser', isNativeShell: false };
  }

  await waitForCordovaReady();

  return {
    kind: 'cordova',
    platformId: window.cordova?.platformId ?? 'cordova',
    isNativeShell: true,
  };
}

export function bindNativeLifecycle(options: {
  pause: () => void;
  resume: () => void;
  back: () => void;
}): () => void {
  if (!window.__CORDOVA_BUILD__) return () => undefined;

  const onPause = () => options.pause();
  const onResume = () => options.resume();
  const onBack = () => options.back();

  document.addEventListener('pause', onPause, false);
  document.addEventListener('resume', onResume, false);
  document.addEventListener('backbutton', onBack, false);

  return () => {
    document.removeEventListener('pause', onPause, false);
    document.removeEventListener('resume', onResume, false);
    document.removeEventListener('backbutton', onBack, false);
  };
}
