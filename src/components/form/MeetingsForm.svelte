<script lang="ts">
	import { createForm } from 'svelte-forms-lib';
	import * as yup from 'yup';
	import { getContext } from 'svelte';
	import { authToken, meetings } from '../../utils/stores';

	const { close } = getContext('simple-modal');

	export let index;
	export let resourceId;
	export let resourceType;
	export let formMethod;

	const { form, errors, handleChange, handleSubmit, isValid, isSubmitting } = createForm({
		initialValues: {
			roomName: $meetings[index].name,
			link: $meetings[index].link,
			endingFlag: Boolean($meetings[index].date_ended)
		},
		validationSchema: yup.object().shape({
			roomName: yup.string().required(),
			link: yup.string().url(),
			endingFlag: yup.boolean()
		}),
		onSubmit: () => {
			return formMethod(resourceId, resourceType, $form, $authToken)
				.then((response) => {
					$meetings[index] = response.data;
					close();
				})
				.catch((error) => alert(error));
		}
	});
</script>

<h2>Edit Meeting Data</h2>

<form on:submit={handleSubmit}>
	<label for="roomName">Room Name</label>
	<input
		name="roomName"
		on:change={handleChange}
		on:blur={handleChange}
		bind:value={$form.roomName}
	/>
	{#if $errors.roomName}
		<small>{$errors.roomName}</small>
	{/if}

	<label for="link">YouTube link</label>
	<input
		type="url"
		name="link"
		on:change={handleChange}
		on:blur={handleChange}
		bind:value={$form.link}
	/>
	{#if $errors.link}
		<small>{$errors.link}</small>
	{/if}

	{#if !$meetings[index].date_ended}
		<label for="endingFlag">End Meeting</label>
		<input
			type="checkbox"
			name="endingFlag"
			on:change={handleChange}
			on:blur={handleChange}
			bind:checked={$form.endingFlag}
		/>
	{/if}

	<button type="submit" disabled={!$isValid}>
		{#if $isSubmitting}
			sending request...
		{:else}
			submit
		{/if}
	</button>
</form>

<style>
	:root {
		--primary-light: #a6f9d6;
		--primary: #5be2a9;
		--primary-dark: #53ce9a;
		--secondary: #1e2145;
		--white: #fff;
		--grey: #e6e6ff;
		--grey-dark: #6d7098;
		--red: #ff6b6b;
	}

	input {
		font-family: inherit;
		font-size: inherit;
		max-width: 400px;
		width: 100%;
		padding: 12px;
		box-sizing: border-box;
		border: 1px solid var(--grey);
		border-radius: 4px;
		transition: all 150ms ease;
		background: var(--white);
	}

	input:focus {
		outline: none;
		box-shadow: 0 0 0 4px rgb(227, 227, 245);
		border-color: var(--grey);
	}

	input:disabled {
		color: #ccc;
	}

	button {
		color: #fff;
		background-color: var(--primary);
		border: none;
		text-transform: uppercase;
		letter-spacing: 1.8px;
		outline: none;
		border-radius: 4px;
		display: block;
		margin-top: 12px;
		line-height: 1.8;
		font-size: 12px;
		padding: 10px 18px;
		min-width: 120px;
		transition: all 150ms ease;
		cursor: pointer;
	}

	button:disabled {
		background-color: var(--grey);
	}

	button:focus:not(:disabled) {
		box-shadow: 0 0 0 4px var(--primary-light);
	}

	button:hover:not(:disabled) {
		background-color: var(--primary-dark);
	}

	label {
		display: block;
		color: var(--grey-dark);
		font-weight: bold;
		margin-top: 20px;
		margin-bottom: 4px;
		text-transform: uppercase;
		font-size: 12px;
		letter-spacing: 1.9px;
		line-height: 2;
	}

	/* used for errors */
	small {
		display: block;
		font-size: 12px;
		color: var(--red);
		margin-top: 10px;
	}
</style>
