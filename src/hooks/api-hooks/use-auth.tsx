import { useMutation } from "@tanstack/react-query";
import authApi from "@/lib/api/auth.api.ts";

export const useLoginQuery = () => useMutation({ mutationFn: authApi.login });
