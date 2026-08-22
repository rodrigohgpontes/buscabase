declare global {
	namespace App {
		interface Error {
			titulo?: string;
			texto?: string;
		}
		interface Locals {
			recorte?: string;
		}
	}
}

export {};
