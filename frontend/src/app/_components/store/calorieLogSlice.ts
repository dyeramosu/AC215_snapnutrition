import { createSlice } from '@reduxjs/toolkit'
import type { PayloadAction } from '@reduxjs/toolkit'
import type { RootState } from './store'


export interface snapNutritionData{
    photoBase64: string | ArrayBuffer | null,
    photoName: string,
    total_calories: number,
    total_fat: number,
    total_carb: number,
    total_protein: number
}

// Define a type for the slice state
interface CalorieLogState {
    value: snapNutritionData[]
}

// Define the initial state using that type
const initialState: CalorieLogState = {
    value: [],
}

export const calorieLogSlice = createSlice({
    name: 'calorieLog',
    // `createSlice` will infer the state type from the `initialState` argument
    initialState,
    reducers: {
        addCalorieEntry: (state, action: PayloadAction<snapNutritionData>) => {
            state.value = [...state.value, action.payload]
        }
    }
})

export const { addCalorieEntry } = calorieLogSlice.actions

export const selectCalorieLog = (state: RootState) => state.calorieLog.value

const calorieLogReducer = calorieLogSlice.reducer
export default calorieLogReducer
