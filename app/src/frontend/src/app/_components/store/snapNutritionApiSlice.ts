import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";


export interface countCaloriesResponse{
    calories: number,
    total_mass_g: number,
    fat_g: number,
    carbs_g: number,
    protein_g: number
}
const baseUrl = process.env.NEXT_PUBLIC_SNAP_NUTRITION_BASE_URL

export const snapNutritionApi = createApi({
    reducerPath: 'snapNutritionApi',
    baseQuery: fetchBaseQuery({baseUrl}),
    endpoints: (builder) => ({
        postFoodPic: builder.mutation<countCaloriesResponse, FormData>({
            query: (body) => ({
                url:  "/predict",
                //url:  "/countCalories",
                method: "POST",
                body
            }),
        }),
    })
})


export const { usePostFoodPicMutation } = snapNutritionApi
