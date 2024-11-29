import { Header } from "./header";

export const Layout = ({ children }) =>{
	return <div className="h-dvh w-screen bg-white flex flex-col">
		<Header />
		<main className="grow flex flex-col w-full">
			{children}
		</main>
	</div>
};