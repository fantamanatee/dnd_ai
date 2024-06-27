const path = require('path');

module.exports = {
  mode: 'development',  // Set to 'production' for minified output
  entry: './src/scripts/main.ts',  // Entry point of your TypeScript application
  output: {
    filename: 'bundle.js',  // Output bundle file name
    path: path.resolve(__dirname, 'dist'),  // Output directory
  },
  resolve: {
    extensions: ['.ts', '.tsx', '.js'],  // Resolve TypeScript and JavaScript files
  },
  module: {
    rules: [
      {
        test: /\.ts$/,  // Apply loader on .ts files
        use: 'ts-loader',  // Use ts-loader for TypeScript files
        exclude: /node_modules/,
      },
      {
        test: /\.css$/,  // Apply loader on .css files
        use: ['style-loader', 'css-loader'],  // Use style-loader and css-loader for CSS files
      },
    ],
  },
};