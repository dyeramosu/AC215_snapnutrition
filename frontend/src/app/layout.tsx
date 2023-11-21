'use client'
import { Inter } from 'next/font/google'
import './globals.css'
import { Provider } from "react-redux";
import { store } from "@/app/_components/store/store";
import Header from "@/app/_components/header/header";
import styles from "@/app/page.module.css";
import { Box, Stack } from "@mui/material";

const inter = Inter({ subsets: ['latin'] })

import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import React from "react";

const darkTheme = createTheme({
    palette: {
        mode: 'light',
    },
});


export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
      <ThemeProvider theme={darkTheme}>
          <CssBaseline />
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
      </ThemeProvider>

  )
}
