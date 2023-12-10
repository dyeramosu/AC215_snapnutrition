import { configureStore } from '@reduxjs/toolkit'
import { snapNutritionApi } from "@/app/_components/store/snapNutritionApiSlice";
import { setupListeners } from "@reduxjs/toolkit/query";
import calorieLogReducer from "@/app/_components/store/calorieLogSlice";

export const store = configureStore({
    reducer: {
        calorieLog: calorieLogReducer,
        [snapNutritionApi.reducerPath]: snapNutritionApi.reducer,
    },
    middleware: (getDefaultMiddleware) =>
        getDefaultMiddleware().concat(snapNutritionApi.middleware),
})

setupListeners(store.dispatch)

export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch
