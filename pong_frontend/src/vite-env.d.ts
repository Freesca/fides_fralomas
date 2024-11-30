/// <reference types="vite/client" />

interface ImportMetaEnv {
	readonly USER_SERVICE_URL: string
	readonly MATCHMAKING_SERVICE_URL: string
	// more env variables...
}

interface ImportMeta {
	readonly env: ImportMetaEnv
}