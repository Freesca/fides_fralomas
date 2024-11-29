/* eslint-disable @typescript-eslint/no-explicit-any */
/* eslint-disable @typescript-eslint/no-unsafe-argument */
/* eslint-disable @typescript-eslint/no-unsafe-member-access */
/* eslint-disable @typescript-eslint/no-unsafe-assignment */
import { useRef, useState } from "react";

export default function LoginPage() {

	const [waitingFor2fa, setWaitingFor2fa] = useState(false);
	const [username, setUsername] = useState("");
	const [errorMsg, setErrorMsg] = useState("");

	const usernameRef = useRef<HTMLInputElement>(null);
	const passwordRef = useRef<HTMLInputElement>(null);
	const twofaRef = useRef<HTMLInputElement>(null);

	const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
		e.preventDefault();

		if (waitingFor2fa) {
			const code = twofaRef.current?.value;

			let req;
			try {
				// TODO: change to prod
				req = await fetch("http://localhost:9003/verify-otp/", {
					method: "POST",
					body: JSON.stringify({
						username: username,
						otp_code: code
					}),
					headers: {
						"content-type": "application/json",
					}
				});
			} catch (e) {
				console.error(e);
				setErrorMsg(`An Error occurred: ${e}`)
				return;
			}
			const json: any = await req.json();

			if (req.ok) {
				setErrorMsg("");
				console.error(json);
				// setWaitingFor2fa(false);
			} else {
				console.log(json);
			}

			return;
		}


		if (usernameRef.current?.value && passwordRef.current?.value) {
			['email', 'username', 'password'].forEach(id => {
				const el = document.querySelector(`div#${id}_errors`);
				if (el) {
					el.innerHTML = "";
				}
			});

			const username = usernameRef.current?.value;
			const password = passwordRef.current?.value;

			const body = {
				username,
				password,
			}

			let req;
			try {
				// TODO: change to prod
				req = await fetch("http://localhost:9003/login/", {
					method: "POST",
					body: JSON.stringify(body),
					headers: {
						"content-type": "application/json",
					}
				});
			} catch (e) {
				console.error(e);
				setErrorMsg(`An Error occurred: ${e}`)
				return;
			}

			const json: any = await req.json();

			if (req.ok) {
				setErrorMsg("");
				setWaitingFor2fa(false);
			} else {
				setUsername(username);
				if (req.status === 400){
					setWaitingFor2fa(true);
				}
				console.error("Error: ", json);
				setErrorMsg(json?.detail ?? json?.message ?? "An error occurred. Try again later");
				return;
			}
			console.log(req);
		}
	};


	return (
		<div className="flex flex-col w-full h-full justify-center items-center">
			<h1>Login</h1>

			<form onSubmit={handleSubmit} className="flex flex-col items-center justify-center gap-4 px-6 py-4 max-w-lg w-1/2 bg-neutral-200 rounded shadow-md">
				<div>
					<span className="text-red-500">{errorMsg}</span>
				</div>
				{/* <div className="flex flex-col gap-2 w-full">
					<label htmlFor="email">Email</label>
					<input id="email" ref={emailRef} type="email" name="email" placeholder="email" className="w-full outline-none text-xl rounded p-1" />
					<div id="email_errors" className="flex items-center gap-2 flex-col text-red-600">

					</div>
				</div> */}
				<div className="flex flex-col gap-2 w-full">
					<label htmlFor="username">Username</label>
					<input id="username" ref={usernameRef} type="text" name="username" placeholder="username" className="w-full outline-none text-xl rounded p-1" />
					<div id="username_errors" className="flex items-center gap-2 flex-col text-red-600">

					</div>
				</div>
				<div className="flex flex-col gap-2 w-full">
					<label htmlFor="password">Password</label>
					<input id="password" ref={passwordRef} type="password" name="password" placeholder="password" className="w-full outline-none text-xl rounded p-1" />
					<div id="password_errors" className="flex items-center gap-2 flex-col text-red-600">

					</div>
				</div>


				{
					waitingFor2fa && (<div>
						<label htmlFor="2fa">2FA code</label>
						<input ref={twofaRef} type="text" name="2fa" placeholder="2FA code" className="w-full outline-none text-xl rounded p-1" />
						<div id="2fa_errors" className="flex items-center gap-2 flex-col text-red-600">

						</div>
					</div>)
				}

				<button type="submit" className="bg-blue-200 hover:bg-blue-300 font-bold py-2 px-4 rounded">
					Login
				</button>
			</form>

		</div>
	);
}
