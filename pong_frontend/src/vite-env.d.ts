/// <reference types="vite/client" />

interface ImportMetaEnv {
	readonly VITE_USER_API_URL: string
	readonly VITE_MATCHMAKING_SERVICE_URL: string
	readonly VITE_MATCH_WS_URL: string
	// more env variables...
}

interface ImportMeta {
	readonly env: ImportMetaEnv
}