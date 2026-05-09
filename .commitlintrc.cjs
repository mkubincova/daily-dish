module.exports = {
	extends: ["@commitlint/config-conventional"],
	rules: {
		// Header rules stay strict (changelog parsers care). Body wrap is off so
		// prose-bullet commit bodies (the /commit-skill style) aren't rejected.
		"body-max-line-length": [0, "always"],
		"footer-max-line-length": [0, "always"],
	},
};
