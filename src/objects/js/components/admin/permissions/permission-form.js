import React, { useEffect, useState } from "react";

import { CheckboxInput, TextInput, SelectInput } from "../../forms/inputs";
import { versionAuthFields } from "./auth-fields";
import {SearchableSelectInput} from "../../forms/searchable-select-input";


const PermissionForm = ({objectFields, tokenChoices, objecttypeChoices, modeChoices, formData}) => {
    const {values, errors} = formData;
    const [mode, setMode]  = useState(values["mode"]);
    const [useFields, setUseFields] = useState(values["use_fields"]);
    const [objectType, setObjectType] = useState(values["object_type"]);
    if (!values["fields"]) {
        values["fields"] = "{}"
    }

    const [fields, setFields] = useState( JSON.parse(values["fields"]) || {} )
    const [dataFieldChoices, setDataFieldChoices] = useState({});

    const fetchObjecttypeVersions = (objecttype_id) => {
        fetch(`/api/v2/objecttypes/${objecttype_id}/versions`, {
            method: 'GET',
            credentials: 'same-origin',
            headers: {
                'Accept': 'application/json',
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`Error ${response.status}: ${response.statusText}`);
            }
            return response.json();
        })
        .then(response_data => {
            const results = response_data.results || response_data;

            if (Array.isArray(results) && results.length > 0) {
                const objecttypes = {
                    [objecttype_id]: results.reduce((acc, version) => {
                        const properties = Object.keys(version?.jsonSchema?.properties || {});
                        acc[version.version] = properties.reduce((propsAcc, prop) => {
                            propsAcc[prop] = `record__data__${prop}`;
                            return propsAcc;
                        }, {});
                        return acc;
                    }, {})
                };

                setDataFieldChoices(objecttypes);
            }
        })
        .catch(error => {
            console.error('An error occurred while fetching the Objecttype versions:', error);
        });
    };
    useEffect(() => {
        if (objectType) {
            fetchObjecttypeVersions(objectType);
        }
    }, [objectType]);
    
    return (
     <fieldset className="module aligned">
        <div className="form-row">
            <SelectInput
                name="token_auth"
                id="id_token_auth"
                label="Token auth:"
                choices={tokenChoices}
                initialValue={values["token_auth"]}
                errors={errors["token_auth"]}
            />
        </div>

        <div className="form-row">
            <SearchableSelectInput
                name="object_type"
                id="id_object_type"
                label="Object type:"
                choices={objecttypeChoices}
                helpText="Changing the Object type will not maintain the previously selected authorization fields."
                initialValue={values["object_type"]}
                errors={errors["object_type"]}
                onChange={(value) => {
                    setObjectType(value);
                    setFields({});
                }}
            />
        </div>

        <div className="form-row">
            <SelectInput
                name="mode"
                id="id_mode"
                label="Mode:"
                choices={modeChoices}
                initialValue={mode}
                errors={errors["mode"]}
                onChange={(value) => {
                    setMode(value);
                    if (value === "read_and_write") {
                        setUseFields(false);
                    }
                }}
            />

        </div>

        <div className="form-row">
            <CheckboxInput
                name="use_fields"
                id="id_use_fields"
                label="Use field-based authorization"
                disabled={!mode || mode === "read_and_write" || Object.keys(dataFieldChoices || {}).length === 0}
                value={useFields}
                onChange={(value) => {setUseFields(value)}}
            />
        </div>

        <TextInput
                name="fields"
                id="id_fields"
                hidden={true}
                value={useFields ? JSON.stringify(fields) : ""}
        />

        { useFields && dataFieldChoices && objectType in dataFieldChoices ?

            <div className="form-row">
                <label htmlFor="id_selected_fields">Fields:</label>
                <div id="id_selected_fields" className="permission-fields">
                    { versionAuthFields(objectType, objectFields, dataFieldChoices, fields, setFields) }
                </div>
            </div>

            : null
        }

     </fieldset>
    );
};


export { PermissionForm };
