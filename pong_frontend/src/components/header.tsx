import { useSession } from 'next-auth/react';
import Link from 'next/link';
import { useRouter } from 'next/router';
import { useEffect } from 'react';
import { AiOutlineUser } from 'react-icons/ai'

export const Header = () => {
	const sessh = useSession();
	const router = useRouter();

	useEffect(()=>{

		if (router.pathname !== "/login" && router.pathname !== "/register") {
			if (sessh.status !== "authenticated") {
				router.push("/login");
			}
		}
	}, [sessh.status]);

	return <header className="flex items-center h-20 bg-white w-full px-8 py-2 font-mono">
		<Link href={"/"}>
			<h1>Pong</h1>
		</Link>


		<span className='flex-grow'></span>

		<div className='flex flex-col items-center gap-2'>
			<AiOutlineUser />
			{sessh.status === "authenticated"
				? <div>
					{sessh.data.user.name}
				</div>
				: <Link href="/login">
					Login
				</Link>
			}
		</div>
	</header>
}