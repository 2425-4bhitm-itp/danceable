// Generated using webpack-cli https://github.com/webpack/webpack-cli

const path = require("path");
const HtmlWebpackPlugin = require("html-webpack-plugin");
const MiniCssExtractPlugin = require("mini-css-extract-plugin");

const isProduction = process.env.NODE_ENV == "production";


const stylesHandler = isProduction ? MiniCssExtractPlugin.loader : "style-loader";


const config = {
  entry: {
    main: "./src/index.ts",
    analysis: "./src/admin/analysis.ts",
  },
  output: {
    path: path.resolve(__dirname, "dist")
  },
  devServer: {
    static: {
      directory: path.join(__dirname, "/")
    },
    compress: true,
    port: 4200,
    proxy: [
      {
        context: ["/api"],
        target: "http://127.0.0.1:8080",
        changeOrigin: true,
        pathRewrite: { "^/api": "" }
      }
    ],
    historyApiFallback: {
      rewrites: [
        { from: /^\/$/, to: "/index.html" },
        { from: /^\/analysis$/, to: "/analysis.html" },
      ],
    },
  },
  plugins: [
    new HtmlWebpackPlugin({
      template: "./src/index.html",
      filename: "index.html",
      chunks: ["main"]
    }),
    new HtmlWebpackPlugin({
      template: "./src/admin/analysis.html",
      filename: "analysis.html",
      chunks: ["analysis"]
    })

    // Add your plugins here
    // Learn more about plugins from https://webpack.js.org/configuration/plugins/
  ],
  module: {
    rules: [
      {
        test: /\.(ts|tsx)$/i,
        loader: "ts-loader",
        exclude: ["/node_modules/"]
      },
      {
        test: /\.css$/i,
        include: path.resolve(__dirname, "src"),
        use: ["style-loader", "css-loader", "postcss-loader"]
      },
      {
        test: /\.(eot|svg|ttf|woff|woff2|png|jpg|gif)$/i,
        type: "asset"
      }

      // Add your rules for custom modules here
      // Learn more about loaders from https://webpack.js.org/loaders/
    ]
  },
  resolve: {
    extensions: [".tsx", ".ts", ".jsx", ".js", "..."]
  }
};

module.exports = () => {
  if (isProduction) {
    config.mode = "production";

    config.plugins.push(new MiniCssExtractPlugin());


  } else {
    config.mode = "development";
  }
  return config;
};