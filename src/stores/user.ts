import {defineStore} from "pinia";
import {ref} from "vue";
import {instance} from "@api/axios.ts";
import usersApi from "@api/users.ts";

export interface User {
    id: string
    email: string
    role: string
    is_active: boolean
}

export const useUserStore = defineStore('user', () => {
    const users = ref<User[] | null>(null)

    const getUsers = async () => {
        const response = await instance.get(usersApi.getUsers);
        users.value = response.data;
    }

    const createUser = async (_email: string, _password: string, _role: string) => {
        await instance.post(usersApi.createUser, {email: _email, password: _password, role: _role});
        await getUsers();
    }

    const deleteUser = async (_id: string) => {
        await instance.delete(usersApi.deleteUser(_id));
        await getUsers();
    }

    const changeUserRole = async (_id: string, _role: string) => {
        await instance.put(usersApi.changeUserRole(_id), {role: _role});
        await getUsers();
    }

    const activateUser = async (_id: string) => {
        await instance.put(usersApi.activateUser(_id));
        await getUsers();
    }

    return {users, getUsers, createUser, deleteUser, changeUserRole, activateUser};
});