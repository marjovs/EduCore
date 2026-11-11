/**
 * Tailwind do EduCore.
 *
 * O Tailwind procura as classes usadas nos templates e gera só o CSS delas em
 * frontend/static/css/tailwind.css. Depois de mudar classes num template, rode:
 *     npm run css          (gera uma vez)
 *     npm run css:watch    (fica gerando enquanto você edita)
 */
module.exports = {
  content: ["./frontend/templates/**/*.html"],
  // O modo escuro é feito por frontend/static/css/tema-escuro.css,
  // ativado pela classe "dark" no <html>.
  darkMode: "class",
  theme: {
    extend: {},
  },
  plugins: [],
};
