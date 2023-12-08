import { createTheme } from '@material-ui/core/styles';

const Theme = createTheme({
    palette: {
        primary: {
          main: '#42a5f5',
          // light: will be calculated from palette.primary.main,
          // dark: will be calculated from palette.primary.main,
          // contrastText: will be calculated to contrast with palette.primary.main
        },
        secondary: {
          main: '#E0C2FF',
          light: '#F5EBFF',
          // dark: will be calculated from palette.secondary.main,
          contrastText: '#47008F',
        },
      },
    typography: {
        useNextVariants: true,
        h6: {
            color: "#1e90ff",
            fontSize: "1.1rem",
            fontFamily: "Roboto, Helvetica, Arial, sans-serif",
            fontWeight: 800
        },
        h5: {
            color: "#1e90ff",
            fontSize: "1.2rem",
            fontFamily: "Roboto, Helvetica, Arial, sans-serif",
            fontWeight: 800
        },
        h4: {
            color: "#1e90ff",
            fontSize: "1.8rem",
            fontFamily: "Roboto, Helvetica, Arial, sans-serif",
            fontWeight: 900
        },
    },
    overrides: {
        MuiOutlinedInput: {
            root: {
                backgroundColor: "#ffffff",
                position: "relative",
                borderRadius: "4px",
            }
        },
    }
});

export default Theme;