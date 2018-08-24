import React from 'react';
import { Icon, Button, Upload } from 'antd';

class ResNetImageRecon extends React.Component {

    constructor(props) {
        super(props);

        this.submitAction = this.submitAction.bind(this);
        this.state = {
            fileUploaded: false,
            file: undefined,
            fileReader: undefined,

            method_options: [
                {
                    name: 'Select Method',
                    value: null,
                },
                {
                    name: 'Flowers',
                    value: 'flowers',
                },
                {
                    name: 'Dogs',
                    value: 'dogs',
                },
                {
                    name: 'Cars',
                    value: 'cars',
                },
            ],
            method_value: 'flowers',

            model_options: [
                {
                    name: 'Select Model',
                    value: null,
                },
                {
                    name: 'ResNet152',
                    value: 'ResNet152',
                },
                {
                    name: 'ResNet18',
                    value: 'ResNet18',
                },
            ],
            model_value: 'ResNet152',
        };

        this.MethodhandleChange = this.MethodhandleChange.bind(this);
        this.ModelhandleChange = this.ModelhandleChange.bind(this);

    }

    isComplete() {
        if (this.props.jobResult === undefined)
            return false;
        else {
            return true;
        }
    }

    processFile(file) {
        let reader = new FileReader();

        reader.onload = (e => {
            this.setState({
                fileUploaded: true,
                file: file,
                fileReader: reader,
            });
        });

        reader.readAsDataURL(file);
    }

    submitAction() {
        this.props.showModalCallback(this.props.callModal);
        this.props.callApiCallback(this.state.method_value, {
            model: this.state.model_value,
            img_path: this.state.fileReader.result.split(',')[1],
        });
    }

    MethodhandleChange(event) {
        this.setState({ method_value: event.target.value });
    };

    ModelhandleChange(event) {
        this.setState({ model_value: event.target.value });
    };

    renderForm() {
        return (
            <React.Fragment>
                <div>
                    <React.Fragment>
                        <div>
                            <table style={{ width: 30 }}>
                                <tbody>
                                    <tr>
                                        <td>Set:</td>
                                        <td>
                                            <select onChange={this.MethodhandleChange} value={this.state.method_value}>
                                                {this.state.method_options.map(item => (
                                                    <option key={item.value} value={item.value}>
                                                        {item.name}
                                                    </option>
                                                ))}
                                            </select>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td>Model:</td>
                                        <td>
                                            <select onChange={this.ModelhandleChange} value={this.state.model_value}>
                                                {this.state.model_options.map(item => (
                                                    <option key={item.value} value={item.value}>
                                                        {item.name}
                                                    </option>
                                                ))}
                                            </select>
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </React.Fragment>
                    {
                        !this.state.fileUploaded &&
                        <React.Fragment>
                            <br />
                            <br />
                            <Upload.Dragger name="file" accept=".jpg,.jpeg,.png" beforeUpload={(file) => { this.processFile(file); return false; }} >
                                <p className="ant-upload-drag-icon">
                                    <Icon type="inbox" />
                                </p>
                                <p className="ant-upload-text">Click for file-chooser dialog or drag a file to this area to be analyzed.</p>
                            </Upload.Dragger>
                        </React.Fragment>
                    }
                    <table><tbody>
                        <tr>
                            <td><b>File:</b></td>
                            <td>{this.state.file ? `${this.state.file.name}` : '(not uploaded)'}</td>
                        </tr>
                    </tbody>
                    </table>

                    <br />
                    <br />
                    {
                        this.state.fileUploaded &&
                        <img src={this.state.fileReader.result} />
                    }
                    <br />
                    <br />
                    <Button type="primary" onClick={() => { this.submitAction(); }} disabled={!this.state.fileUploaded} >Call Agent API</Button>
                </div>
            </React.Fragment >
        )
    }

    renderComplete() {
        let jsonResult = this.props.jobResult['result'];
        let delta_time = jsonResult['delta_time'];
        if (delta_time === undefined) delta_time = '-1';
        let jsonTop5 = jsonResult['top_5'];
        if (jsonTop5 === undefined) jsonTop5 = { '-1': jsonResult };
        let arr = [];
        Object.keys(jsonTop5).forEach(function (key) {
            arr.push(key);
        });

        return (
            <div>
                <div>
                    <ul>{arr.map(item => <Json2List key={item} label={item} value={jsonTop5[item]} />)}</ul>
                    Execution time: {delta_time}s
                </div>
            </div>
        );
    }

    renderDescription() {
        return (
            <div>
                <p>
                    A service that uses Residual Networks to classify images of flowers, dogs or cars.
                </p>
            </div>
        )
    }

    render() {
        if (this.isComplete())
            return (
                <div>
                    {this.renderDescription()}
                    {this.renderComplete()}
                </div>
            );
        else
            return (
                <div>
                    {this.renderDescription()}
                    {this.renderForm()}
                </div>
            )
    }
}

class Json2List extends React.Component {
    render() {
        return <li>{this.props.label + " - " + this.props.value}</li>;
    }
}

export default ResNetImageRecon;