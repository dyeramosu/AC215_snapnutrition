'use client'
import { Inter } from 'next/font/google'
import './globals.css'
import { Provider } from "react-redux";
import { store } from "@/app/_components/store/store";
import Header from "@/app/_components/header/header";
import styles from "@/app/page.module.css";
import { Box, Stack } from "@mui/material";

const inter = Inter({ subsets: ['latin'] })

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
      <Provider store={store}>
          <html lang="en">

            <body className={inter.className}>
                <Header />
                <Box m={"auto"} className={styles.test}>
                    <Stack>
                        <main>{children}</main>
                    </Stack>
                </Box>
            </body>
          </html>
      </Provider>
  )
}
