import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";


export interface countCaloriesBody{
    photoBase64: string | ArrayBuffer | null,
    photoName: string
}
export interface countCaloriesResponse{
    photoName: string,
    total_calories: number,
    total_fat: number,
    total_carb: number,
    total_protein: number
}
const baseUrl = process.env.NEXT_PUBLIC_SNAP_NUTRITION_BASE_URL

export const snapNutritionApi = createApi({
    reducerPath: 'snapNutritionApi',
    baseQuery: fetchBaseQuery({baseUrl}),
    endpoints: (builder) => ({
        postFoodPic: builder.mutation<countCaloriesResponse, countCaloriesBody>({
            query: (body) => ({
                url:  "/countCalories",
                method: "POST",
                body
            }),
        }),
    })
})


export const { usePostFoodPicMutation } = snapNutritionApi
